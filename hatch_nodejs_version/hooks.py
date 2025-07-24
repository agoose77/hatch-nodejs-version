# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
from hatchling.plugin import hookimpl

from .metadata_source import NodeJSMetadataHook
from .version_source import NodeJSVersionSource


@hookimpl
def hatch_register_version_source():
    return NodeJSVersionSource


@hookimpl
def hatch_register_metadata_hook():
    return NodeJSMetadataHook
