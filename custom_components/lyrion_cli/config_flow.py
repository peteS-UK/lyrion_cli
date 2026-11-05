"""Config flow for Lyrion CLI."""

from homeassistant import config_entries

from .const import DOMAIN


class LyrionCLIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        """Invoked when a user initiates a flow via the user interface."""
        if user_input is not None:
            return self.async_create_entry(title="Lyrion CLI", data={"None": "None"})

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(step_id="user")
