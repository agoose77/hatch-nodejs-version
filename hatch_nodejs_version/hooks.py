# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
from hatchling.plugin import hookimpl

from .version_source import NodeJSVersionSource
from .metadata_source import NodeJSMetadataHook


@hookimpl
def hatch_register_version_source():
    return NodeJSVersionSource


@hookimpl
def hatch_register_metadata_hook():
    return NodeJSMetadataHook
