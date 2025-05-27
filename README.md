# Lyrion CLI Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![maintained](https://img.shields.io/maintenance/yes/2025.svg)](#)
[![maintainer](https://img.shields.io/badge/maintainer-%20%40petes--UK-blue.svg)](#)
[![version](https://img.shields.io/github/v/release/peteS-UK/lyrion_cli)](#)

This repo contains a Home Assistant integration to add two actions for the Lyrion/Squeezebox CLI/API. These duplicate the call_method and call_query actions which already exist in the core Squeezebox integration, which we believe at some point may be depreacted, due to a desire from the core Home Assistant team to restrict access to complex APIs in favour of more use specific actions. The new actions are called method and query. The only difference is that the new query action will return its result using the modern response variable mechanism, rather than call_query which stored the result in a state attribute.

For a query action, you can target either a Squeezebox device, or a Squeezebox media player entity. Only one device or entity may be targetted by each query. For a method action, you can target multiple devices or entities, or a combination of both.

This is a companion component to the official [Squeezebox](https://www.home-assistant.io/integrations/squeezebox/) integration. It uses the LMS and player information that is created and maintained by the official component, rather than managing a duplicate set of this information itself. As such, it's dependent on the official installation being installed and configured.

## Installation

The preferred installation approach is via Home Assistant Community Store - aka [HACS](https://hacs.xyz/).

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=peteS-UK&repository=lyrion_cli&category=integration)

If you want to download the integration manually, create a new folder called lyrion_cli under your custom_components folder in your config folder. If the custom_components folder doesn't exist, create it first. Once created, download the files from the [github repo](https://github.com/peteS-UK/lyrion_cli/tree/main/custom_components/lyrion_cli) into this lyrion_cli folder.

Once downloaded either via HACS or manually, restart your Home Assistant server.

## Configuration

To enable the integration, add the integration under Settings, Devices & Services.

## Usage

Usage is the same as call_method and call_query. See the docs at https://www.home-assistant.io/integrations/squeezebox/#actions
