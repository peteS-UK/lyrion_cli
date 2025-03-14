# Lyrion CLI Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This repo contains a Home Assistant integration to add two actions for the Lyrion/Squeezebox CLI/API.  These duplicate the call_method and call_query actions which already exist in the core Squeezebox integration, which we believe at some point will be depreacted.  The new actions are called method and query.  The only difference is that the new query action will return its result using the modern response variable mechanism, rather than call_query which stored the result in a state attribute.

## Installation

The preferred installation approach is via Home Assistant Community Store - aka [HACS](https://hacs.xyz/).  The repo is installable as a [Custom Repo](https://hacs.xyz/docs/faq/custom_repositories) via HACS.

If you want to download the integration manually, create a new folder called lyrion_cli under your custom_components folder in your config folder.  If the custom_components folder doesn't exist, create it first.  Once created, download the 3 files from the [github repo](https://github.com/peteS-UK/lyrion_cli/tree/main/custom_components/lyrion_cli) into this lyrion_cli folder.

Once downloaded either via HACS or manually, restart your Home Assistant server.

## Configuration

To enable the integration, add the following line to your configuration.yaml file, typically in your /config folder.

```yaml
lyrion_cli:
```

Once updated, restart your Home Assistant server again to enable the integration.

## Usage

Usage is the same as call_method and call_query.  See the docs at https://www.home-assistant.io/integrations/squeezebox/#actions
