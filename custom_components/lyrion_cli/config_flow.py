import logging

from homeassistant import config_entries

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "lyrion_cli"
_LOGGER = logging.getLogger(__name__)


class LyrionCLIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Invoked when a user initiates a flow via the user interface."""
        if user_input is not None:
            return self.async_create_entry(title="Lyrion CLI", data={"None": "None"})

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(step_id="user")
