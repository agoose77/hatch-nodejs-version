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
# - Only support three-component release and prerelease segments
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
"""

# The NodeJS-aware Python version regex
# This is very similar to `packaging.version.VERSION_PATTERN`, with a few changes:
# - Only support three-component release and prerelease segments
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
   )
"""


class NodeJSVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "nodejs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__path = None

    @staticmethod
    def node_version_to_python(version: str) -> str:
        # NodeJS version strings are a near superset of Python version strings
        match = re.match(
            r"^\s*" + NODE_VERSION_PATTERN + r"\s*$",
            version,
            re.VERBOSE | re.IGNORECASE,
        )
        if match is None:
            raise ValueError(f"Version {version!r} did not match regex")

        parts = ["{major}.{minor}.{patch}".format_map(match)]

        if match["pre"]:
            if match["pre_n"] is None:
                parts.append("{pre_l}".format_map(match))
            else:
                parts.append("{pre_l}{pre_n}".format_map(match))

        return "".join(parts)

    @staticmethod
    def python_version_to_node(version: str) -> str:
        # NodeJS version strings are a near superset of Python version strings
        match = re.match(
            r"^\s*" + PYTHON_VERSION_PATTERN + r"\s*$",
            version,
            re.VERBOSE | re.IGNORECASE,
        )
        if match is None:
            raise ValueError(f"Version {version!r} did not match regex")

        parts = ["{major}.{minor}.{patch}".format_map(match)]

        if match["pre"]:
            if match["pre_n"] is None:
                parts.append("-{pre_l}".format_map(match))
            else:
                parts.append("-{pre_l}{pre_n}".format_map(match))

        return "".join(parts)

    @property
    def path(self):
        if self.__path is None:
            version_file = self.config.get("path", "package.json")
            if not isinstance(version_file, str):
                raise TypeError(
                    "Option `path` for build hook `{}` must be a string".format(
                        self.PLUGIN_NAME
                    )
                )

            self.__path = version_file

        return self.__path

    def get_version_data(self):
        path = os.path.normpath(os.path.join(self.root, self.path))
        if not os.path.isfile(path):
            raise OSError(f"file does not exist: {self.path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {"version": self.node_version_to_python(data["version"])}

    def set_version(self, version: str, version_data):
        path = os.path.normpath(os.path.join(self.root, self.path))
        if not os.path.isfile(path):
            raise OSError(f"file does not exist: {self.path}")

        with open(path, "r") as f:
            data = json.load(f)

        data["version"] = self.python_version_to_node(version)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
