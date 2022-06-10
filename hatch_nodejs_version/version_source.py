# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import json
import os
import re
from hatchling.version.source.plugin.interface import VersionSourceInterface


# The Python-aware NodeJS version regex
# This is very similar to `packaging.version.VERSION_PATTERN`, with a few changes:
# - Don't accept underscores
# - Require - to indicate prerelease
NODE_VERSION_PATTERN = r"""
    (?P<major>[0-9]+)                                 # major
    \.
    (?P<minor>[0-9]+)                                 # minor
    \.
    (?P<patch>[0-9]+)                                 # patch
    (?P<pre>                                          # pre-release
        -
        (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
        [-\.]?
        (?P<pre_n>[0-9]+)?
    )?
    (?P<post>                                         # post release
    (?:-(?P<post_n1>[0-9]+))
    |
    (?:
        [-\.]?
        (?P<post_l>post|rev|r)
        [-\.]?
        (?P<post_n2>[0-9]+)?
    )
    )?
    (?P<dev>                                              # dev release
        [-\.]?
        (?P<dev_l>dev)
        [-\.]?
        (?P<dev_n>[0-9]+)?
    )?
"""

# The NodeJS-aware Python version regex
# This is very similar to `packaging.version.VERSION_PATTERN`, with a few changes:
# - Don't accept epochs or local packages
# - Require three components
PYTHON_VERSION_PATTERN = r"""
   v?
   (?:
       (?P<major>[0-9]+)                                 # major
       \.
       (?P<minor>[0-9]+)                                 # minor
       \.
       (?P<patch>[0-9]+)                                 # patch
       (?P<pre>                                          # pre-release
           [-_\.]?
           (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
           [-_\.]?
           (?P<pre_n>[0-9]+)?
       )?
       (?P<post>                                         # post release
           (?:-(?P<post_n1>[0-9]+))
           |
           (?:
               [-_\.]?
               (?P<post_l>post|rev|r)
               [-_\.]?
               (?P<post_n2>[0-9]+)?
           )
       )?
       (?P<dev>                                          # dev release
           [-_\.]?
           (?P<dev_l>dev)
           [-_\.]?
           (?P<dev_n>[0-9]+)?
       )?
   )
"""


class NodeJSVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "nodejs"

    def node_version_to_python(self, version: str) -> str:
        # NodeJS version strings are a near superset of Python version strings
        # We opt to read the pre.post.dev from the NodeJS pre field
        match = re.match(
            r"^\s*" + NODE_VERSION_PATTERN + r"\s*$",
            version,
            re.VERBOSE | re.IGNORECASE,
        )
        if match is None:
            raise ValueError(f"Version {version!r} did not match regex")

        parts = ["{major}.{minor}.{patch}".format_map(match)]

        if match["pre"]:
            parts.append("{pre_l}{pre_n}".format_map(match))
        if match["post_n1"]:
            parts.append(".post{post_n1}".format_map(match))
        elif match["post_l"]:
            parts.append(".{post_l}{post_n2}".format_map(match))
        if match["dev"]:
            parts.append("{dev_l}{dev_n}".format_map(match))

        return "".join(parts)

    def python_version_to_node(self, version: str) -> str:
        # NodeJS version strings are a near superset of Python version strings
        # We opt to read the pre.post.dev from the NodeJS pre field
        match = re.match(
            r"^\s*" + PYTHON_VERSION_PATTERN + r"\s*$",
            version,
            re.VERBOSE | re.IGNORECASE,
        )
        if match is None:
            raise ValueError(f"Version {node_version!r} did not match regex")

        parts = ["{major}.{minor}.{patch}".format_map(match)]

        pre_parts = []
        if match["pre"]:
            pre_parts.append("{pre_l}{pre_n}".format_map(match))
        if match["post_n1"]:
            pre_parts.append(".post{post_n1}".format_map(match))
        elif match["post_l"]:
            pre_parts.append(".{post_l}{post_n2}".format_map(match))
        if match["dev"]:
            pre_parts.append("{dev_l}{dev_n}".format_map(match))

        if pre_parts:
            parts.append("-" + "".join(pre_parts))

        return "".join(parts)

    def get_version_data(self):
        relative_path = self.config.get("path", "package.json")
        if not isinstance(relative_path, str):
            raise TypeError("option `path` must be a string")

        path = os.path.normpath(os.path.join(self.root, relative_path))
        if not os.path.isfile(path):
            raise OSError(f"file does not exist: {relative_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {"version": self.node_version_to_python(data["version"]), "path": path}

    def set_version(self, version: str, version_data):
        path = version_data["path"]
        with open(path, "r") as f:
            data = json.load(f)
        data["version"] = self.python_version_to_node(version)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
