"""Example of a custom component exposing a service."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import logging

import aiohttp
import voluptuous as vol

from homeassistant.const import ATTR_COMMAND, CONF_HOST, CONF_PORT
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.typing import ConfigType

TIMEOUT: float = 10.0
ATTR_PARAMETERS = "parameters"

CLI_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_COMMAND): cv.string,
        vol.Optional("device_id"): any,
        vol.Optional("entity_id"): any,
        vol.Optional(ATTR_PARAMETERS): vol.All(
            cv.ensure_list, vol.Length(min=1), [cv.string]
        ),
    }
)


@dataclass
class player:
    """player."""

    mac: str
    lms_ip: str
    lms_https: bool
    lms_port: int
    username: str
    password: str


# The domain of your component. Should be equal to the name of your component.
DOMAIN = "lyrion_cli"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sync service example component."""

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    async def async_get_players(call: ServiceCall):
        devices: DeviceEntry = []
        players: player = []

        if "entity_id" in call.data:
            for entity_id in call.data["entity_id"]:
                entity = entity_registry.async_get(entity_id_or_uuid=entity_id)
                config_entry = hass.config_entries.async_get_entry(
                    entity.config_entry_id
                )

                players.append(
                    player(
                        mac=entity.unique_id,
                        lms_ip=config_entry.data[CONF_HOST],
                        lms_port=config_entry.data[CONF_PORT],
                        lms_https=config_entry.data.get("https"),
                        username=config_entry.data.get("username"),
                        password=config_entry.data.get("password"),
                    )
                )

        if "device_id" in call.data:
            for device_id in call.data["device_id"]:
                # devices.append(dr.async_get(device_id))
                devices.append(device_registry.async_get(device_id))

            for device in devices:
                for config_entry_id in device_registry.async_get(
                    device.via_device_id
                ).config_entries:
                    if (
                        hass.config_entries.async_get_entry(config_entry_id).domain
                        == "squeezebox"
                    ):
                        lms_config_entry = hass.config_entries.async_get_entry(
                            config_entry_id
                        )
                        break

                players.append(
                    player(
                        mac=list(device.connections)[0][1],
                        lms_ip=lms_config_entry.data[CONF_HOST],
                        lms_port=lms_config_entry.data[CONF_PORT],
                        lms_https=config_entry.data.get("https"),
                        username=lms_config_entry.data.get("username"),
                        password=lms_config_entry.data.get("password"),
                    )
                )
        return players

    def ensure_list(item: any) -> list[any]:
        return item if isinstance(item, list) else [item]

    async def async_query(player: player, *command: str):
        session: aiohttp.ClientSession = async_get_clientsession(hass)

        if session is None:
            raise ValueError("async_query() called with Server.session unset")

        auth = (
            None
            if player.username is None or player.password is None
            else aiohttp.BasicAuth(player.username, player.password)
        )

        prefix = "https" if player.lms_https else "http"

        url = f"{prefix}://{player.lms_ip}:{player.lms_port}/jsonrpc.js"
        query_data = json.dumps(
            {"id": "1", "method": "slim.request", "params": [player.mac, command]}
        )

        try:
            async with asyncio.timeout(TIMEOUT):
                response = await session.post(url, data=query_data, auth=auth)

                if response.status != 200:
                    _LOGGER.info(
                        "Query failed, response code: %s Full message: %s",
                        response.status,
                        response,
                    )
                    return None

                result_data = await response.json()

        except aiohttp.ServerDisconnectedError as error:
            # LMS handles an unknown player by abruptly disconnecting
            if player.mac:
                _LOGGER.info(
                    "Query run on unknown player %s, or invalid command", player.mac
                )
            else:
                _LOGGER.error("Failed communicating with LMS(%s): %s", url, type(error))
            return None

        except (TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Failed communicating with LMS(%s): %s", url, type(error))
            return None

        try:
            result = result_data["result"]
            if not isinstance(result, dict):
                _LOGGER.error("Received invalid response: %s", result)
                return None
            return result
        except KeyError:
            _LOGGER.error("Received invalid response: %s", result_data)
        return None

    async def async_query_service(call: ServiceCall) -> None:
        """Call Query."""

        players = await async_get_players(call=call)

        if len(players) == 0:
            raise ServiceValidationError("You must select either a device or entity.")
        if len(players) > 1:
            raise ServiceValidationError("Please choose only 1 device or entity.")

        all_params = [call.data[ATTR_COMMAND]]
        if call.data.get(ATTR_PARAMETERS):
            all_params.extend(ensure_list(call.data[ATTR_PARAMETERS]))
        _LOGGER.debug("Query Params %s", all_params)
        result: ServiceResponse = await async_query(players[0], *all_params)
        _LOGGER.debug("Method result %s", result)
        if result:
            return result
        raise ServiceValidationError("Action returned no result")

    async def async_method_service(call: ServiceCall) -> None:
        """Call Method."""

        players = await async_get_players(call=call)

        if len(players) == 0:
            raise ServiceValidationError(
                "You must select at least one device or entity."
            )

        for player in players:
            all_params = [call.data[ATTR_COMMAND]]
            if call.data.get(ATTR_PARAMETERS):
                all_params.extend(ensure_list(call.data[ATTR_PARAMETERS]))
            _LOGGER.debug("Method Params %s", all_params)
            result: ServiceResponse = await async_query(player, *all_params)
            _LOGGER.debug("Method result %s", result)

            if result != {}:
                raise ServiceValidationError(f"Method {call.data[ATTR_COMMAND]} failed")

        return True

    # Register our service with Home Assistant.
    hass.services.async_register(
        DOMAIN,
        "query",
        async_query_service,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        "method",
        async_method_service,
    )

    # Return boolean to indicate that initialization was successfully.
    return True
