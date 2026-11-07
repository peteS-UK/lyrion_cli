# Lyrion CLI Integration

[![Available in Marketplace](https://img.shields.io/badge/Marketplace-Available-41BDF5)](#installation-with-marketplace)
[![maintained](https://img.shields.io/maintenance/yes/2026.svg)](#)
[![maintainer](https://img.shields.io/badge/maintainer-%20%40petes--UK-blue.svg)](#)
[![version](https://img.shields.io/github/v/release/peteS-UK/lyrion_cli)](#)

This repo contains a Home Assistant integration to add two actions for the Lyrion/Squeezebox CLI/API. These duplicate the call_method and call_query actions which already exist in the core Squeezebox integration, which we believe at some point may be depreacted, due to a desire from the core Home Assistant team to restrict access to complex APIs in favour of more use specific actions. The new actions are called method and query. The only difference is that the new query action will return its result using the modern response variable mechanism, rather than call_query which stored the result in a state attribute.

For a query action, you can target either a Squeezebox device, or a Squeezebox media player entity. Only one device or entity may be targetted by each query. For a method action, you can target multiple devices or entities, or a combination of both.

This is a companion component to the official [Squeezebox](https://www.home-assistant.io/integrations/squeezebox/) integration. It uses the LMS and player information that is created and maintained by the official component, rather than managing a duplicate set of this information itself. As such, it's dependent on the official installation being installed and configured.

## Installation with Marketplace

The [Marketplace](https://www.home-assistant.io/integrations/marketplace/) is built into **Home Assistant 2026.11 and later**; no separate store installation is needed.

1. As an administrator, open **Settings → Marketplace** and accept its first-use notice if prompted.
2. Search for **Lyrion CLI Action** and open its page.
3. Choose **Install**, review the version, then confirm **Install**. Account setup opens when installation finishes; continue with [Configuration](#configuration). A fresh installation does not need a restart.

Existing HACS installations migrate automatically when you upgrade Home Assistant to 2026.11. Your installed integration and updates carry over; you do not need to reinstall it.

## Installation with HACS

For older versions of Home Assistant, you can install via Home Assistant Community Store - aka [HACS](https://hacs.xyz/).  Search for **Lyrion CLI Action** and install the integration.

## Manual Installation
If you want to download the integration manually, create a new folder called lyrion_cli under your custom_components folder in your config folder. If the custom_components folder doesn't exist, create it first. Once created, download the files from the [github repo](https://github.com/peteS-UK/lyrion_cli/tree/main/custom_components/lyrion_cli) into this lyrion_cli folder.

Once downloaded either via HACS or manually, restart your Home Assistant server.

Configuration is done through the Home Assistant UI.  Once you're installed the integration, go into your Integrations (under Settings, Devices & Services), select Add Integration, and choose the Lyrion CLI integration, or click the shortcut button below (requires My Homeassistant configured).

[![Add Integration to your Home Assistant
instance.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=lyrion_cli)

## Configuration

There are no configuration options for the integration since it's a partner integration to Squeezebox.

## Usage

Usage is the same as call_method and call_query. See the docs at https://www.home-assistant.io/integrations/squeezebox/#actions

In addition, the query action supports an additional timeout attribute

| Data attribute | Optional | Description                                                                          |
| -------------- | -------- | ------------------------------------------------------------------------------------ |
| `timeout`      | yes      | The number of seconds to wait before the query times out. The default is 10 seconds. |
