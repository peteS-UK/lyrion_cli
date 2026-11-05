"""Service to call Lyrion CLI commands."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass

import aiohttp
import probatio
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_COMMAND,
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import (
    config_validation as cv,
)
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.typing import ConfigType

from .const import ATTR_PARAMETERS, ATTR_TIMEOUT, CONF_HTTPS, DOMAIN, TIMEOUT

CLI_SCHEMA = probatio.Schema(
    {
        probatio.Required(ATTR_COMMAND): cv.string,
        probatio.Optional(ATTR_DEVICE_ID): probatio.All(cv.ensure_list, [cv.string]),
        probatio.Optional(ATTR_ENTITY_ID): probatio.All(cv.ensure_list, [cv.string]),
        probatio.Optional(ATTR_PARAMETERS): probatio.All(
            cv.ensure_list, probatio.Length(min=1), [cv.string]
        ),
        probatio.Optional(ATTR_TIMEOUT): probatio.Coerce(float),
    }
)


@dataclass
class Player:
    """Player."""

    mac: str
    lms_ip: str
    lms_https: bool | None
    lms_port: int
    username: str | None
    password: str | None


_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lyrion CLI from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the Lyrion CLI services."""

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    async def async_get_players(call: ServiceCall):
        devices: list[DeviceEntry] = []
        players: list[Player] = []

        if ATTR_ENTITY_ID in call.data:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                entity = entity_registry.async_get(entity_id_or_uuid=entity_id)
                if not entity or not entity.config_entry_id:
                    continue
                config_entry = hass.config_entries.async_get_entry(
                    entity.config_entry_id
                )
                if config_entry is None:
                    continue

                players.append(
                    Player(
                        mac=entity.unique_id,
                        lms_ip=config_entry.data[CONF_HOST],
                        lms_port=config_entry.data[CONF_PORT],
                        lms_https=config_entry.data.get(CONF_HTTPS),
                        username=config_entry.data.get(CONF_USERNAME),
                        password=config_entry.data.get(CONF_PASSWORD),
                    )
                )

        if ATTR_DEVICE_ID in call.data:
            for device_id in call.data[ATTR_DEVICE_ID]:
                # devices.append(dr.async_get(device_id))
                device = device_registry.async_get(device_id)
                if isinstance(device, DeviceEntry):
                    devices.append(device)

            for device in devices:
                lms_config_entry: ConfigEntry | None = None
                lms_device = (
                    device_registry.async_get(device.via_device_id)
                    if device.via_device_id
                    else None
                )
                if lms_device is None:
                    continue
                for config_entry_id in lms_device.config_entries:
                    entry_candidate = hass.config_entries.async_get_entry(
                        config_entry_id
                    )
                    if entry_candidate and entry_candidate.domain == "squeezebox":
                        lms_config_entry = entry_candidate
                        break

                if lms_config_entry is None:
                    continue

                players.append(
                    Player(
                        mac=next(iter(device.connections))[1],
                        lms_ip=lms_config_entry.data[CONF_HOST],
                        lms_port=lms_config_entry.data[CONF_PORT],
                        lms_https=lms_config_entry.data.get(CONF_HTTPS),
                        username=lms_config_entry.data.get(CONF_USERNAME),
                        password=lms_config_entry.data.get(CONF_PASSWORD),
                    )
                )
        return players

    async def async_query(player: Player, *command: str, timeout: float | None = None):
        if not timeout:
            timeout = TIMEOUT

        session: aiohttp.ClientSession = async_get_clientsession(hass)
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
            async with asyncio.timeout(timeout):
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

        except TimeoutError:
            raise ServiceValidationError("Query Timed Out")

        except aiohttp.ClientError as error:
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

    async def async_query_service(call: ServiceCall) -> ServiceResponse:
        """Call Query."""

        players = await async_get_players(call=call)

        if len(players) == 0:
            raise ServiceValidationError("You must select either a device or entity.")
        if len(players) > 1:
            raise ServiceValidationError("Please choose only 1 device or entity.")

        all_params = [call.data[ATTR_COMMAND]]
        if call.data.get(ATTR_PARAMETERS):
            all_params.extend(call.data[ATTR_PARAMETERS])
        _LOGGER.debug("Query Params %s", all_params)
        result: ServiceResponse = await async_query(
            players[0], *all_params, timeout=call.data.get(ATTR_TIMEOUT)
        )
        _LOGGER.debug("Query result %s", result)
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
                all_params.extend(call.data[ATTR_PARAMETERS])
            _LOGGER.debug("Method Params %s", all_params)
            result: ServiceResponse = await async_query(player, *all_params)
            _LOGGER.debug("Method result %s", result)

            if result != {}:
                raise ServiceValidationError(f"Method {call.data[ATTR_COMMAND]} failed")

    # Register our service with Home Assistant.
    hass.services.async_register(
        DOMAIN,
        "query",
        async_query_service,
        schema=CLI_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        "method",
        async_method_service,
        schema=CLI_SCHEMA,
    )

    # Return boolean to indicate that initialization was successfully.
    return True
