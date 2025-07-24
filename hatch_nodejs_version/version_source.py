# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import json
import os
import re

from hatchling.version.source.plugin.interface import VersionSourceInterface

PRE_PATTERN = r"""
        (?P<{prefix}pre_l>(a|b|c|rc|alpha|beta|pre|preview))
        [-.]?
        (?P<{prefix}pre_n>[0-9]+)?

"""
DEV_PATTERN = r"""
        dev
        [-.]?
        (?P<{prefix}dev_n>[0-9]+)?
"""

# The Python-aware NodeJS version regex
# This is very similar to `packaging.version.VERSION_PATTERN`, with a few changes:
# - Don't accept underscores
# - Only support four-component release, prerelease, and build segments
# - Require - to indicate prerelease
NODE_VERSION_PATTERN = rf"""
    (?P<major>[0-9]+)                             # major
    \.
    (?P<minor>[0-9]+)                             # minor
    \.
    (?P<patch>[0-9]+)                             # patch
    (?:
      (?P<pre_only>                               # pre-release    
        -
        {PRE_PATTERN.format(prefix="pre_only_")}
      ) | 
      (?P<dev_only>                               # dev
        -
        {DEV_PATTERN.format(prefix="dev_only_")}
      ) |
      (?P<pre_dev>                                # pre-release and dev    
        -
        {PRE_PATTERN.format(prefix="pre_dev_")}
        \.
        {DEV_PATTERN.format(prefix="pre_dev_")}
      )
    )?
    (?:
       \+
       (?P<build>
            [0-9A-Za-z][0-9A-Za-z-_]*            # non-hyphen/dash leading identifier
            (?:
                (?:\.[0-9A-Za-z-_]+)*            # dot-prefixed identifier segments
            \.                                   # Final dot-delimited segment
                [0-9A-Za-z_-]*                   # non-hyphen/dash trailing identifier
                [0-9A-Za-z]
            )?
        )
   )?
"""

# The NodeJS-aware Python version regex
# This is very similar to `packaging.version.VERSION_PATTERN`, with a few changes:
# - Only support five-component release, prerelease, dev, and build segments
PYTHON_VERSION_PATTERN = r"""
   v?
   (?:
       (?P<major>[0-9]+)                           # major
       \.
       (?P<minor>[0-9]+)                           # minor
       \.
       (?P<patch>[0-9]+)                           # patch
       (?P<pre>                                    # pre-release
           [-_.]?
           (?P<pre_l>(alpha|beta|preview|a|b|c|rc|pre))
           [-_.]?
           (?P<pre_n>[0-9]+)?
       )?
       (?P<dev>
           [-_.]?
           dev
           (?P<dev_n>[0-9]+)
       )?
       (?:                                         # local version number
           \+
           (?P<local>
                [0-9A-Za-z][0-9A-Za-z-_]*          # non-hyphen/dash leading identifier
                (?:
                    (?:\.[0-9A-Za-z-_]+)*          # dot-prefixed identifier
                    \.
                    [0-9A-Za-z_-]*                 # non-hyphen/dash trailing identifier
                    [0-9A-Za-z]
                )?
            )
       )?
   )
"""


class NodeJSVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "nodejs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__path = None

    @property
    def path(self):
        if self.__path is None:
            version_file = self.config.get("path", "package.json")
            if not isinstance(version_file, (str, bytes, os.PathLike)):
                raise TypeError(
                    "Option `path` for version source `{}` must be a string".format(
                        self.PLUGIN_NAME
                    )
                )

            self.__path = os.fspath(version_file)

        return self.__path

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

        groups = {}
        for key, value in match.groupdict().items():
            key = re.sub("pre_dev_|pre_only_|dev_only_", "", key)
            if key not in groups:
                groups[key] = value
            elif value is not None:
                groups[key] = value

        del match
        parts = ["{major}.{minor}.{patch}".format_map(groups)]

        if groups["pre_only"] or groups["pre_dev"]:
            if groups["pre_n"] is None:
                parts.append("{pre_l}".format_map(groups))
            else:
                parts.append("{pre_l}{pre_n}".format_map(groups))

        if groups["dev_only"] or groups["pre_dev"]:
            if groups["dev_n"] is None:
                parts.append("dev0")
            else:
                parts.append("dev{dev_n}".format_map(groups))

        if groups["build"]:
            parts.append("+{build}".format_map(groups))

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

        if match["dev"]:
            if match["pre"]:
                parts.append(".dev{dev_n}".format_map(match))
            else:
                parts.append("-dev{dev_n}".format_map(match))

        if match["local"]:
            parts.append("+{local}".format_map(match))
        return "".join(parts)

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

        # Read the original file so we can see if it has a trailing
        # newline character.
        with open(path, "r") as f:
            raw_data = f.read()

        data = json.loads(raw_data)

        data["version"] = self.python_version_to_node(version)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
            if raw_data.endswith("\n"):
                f.write("\n")
