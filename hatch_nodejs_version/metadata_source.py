# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
import os.path
import re
import urllib.parse
from typing import Any, Union

from hatchling.metadata.plugin.interface import MetadataHookInterface

AUTHOR_PATTERN = r"^(?P<name>[^<(]+?)?[ \t]*(?:<(?P<email>[^>(]+?)>)?[ \t]*(?:\((?P<url>[^)]+?)\)|$)"
REPOSITORY_PATTERN = r"^(?:(gist|bitbucket|gitlab|github):)?(.*?)$"
REPOSITORY_TABLE = {
    "gitlab": "https://gitlab.com",
    "github": "https://github.com",
    "gist": "https://gist.github.com",
    "bitbucket": "https://bitbucket.org",
}


class NodeJSMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "nodejs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__path = None
        self.__fields = None
        self.__contributors_as_maintainers = None
        self.__homepage_label = None
        self.__bugs_label = None
        self.__repository_label = None

    @property
    def path(self) -> str:
        if self.__path is None:
            version_file = self.config.get("path", "package.json")
            if not isinstance(version_file, str):
                raise TypeError(
                    "Option `path` for metadata hook `{}` must be a string".format(
                        self.PLUGIN_NAME
                    )
                )

            self.__path = version_file

        return self.__path

    @property
    def fields(self) -> None | set[str]:
        if self.__fields is None:
            fields = self.config.get("fields", None)
            if fields is None:
                self.__fields = None
            else:
                if not (
                    isinstance(fields, list) and all(isinstance(f, str) for f in fields)
                ):
                    raise TypeError(
                        "Option `fields` for metadata hook `{}` "
                        "must be a list of strings".format(self.PLUGIN_NAME)
                    )
                self.__fields = set(fields)
        return self.__fields

    @property
    def contributors_as_maintainers(self) -> bool:
        if self.__contributors_as_maintainers is None:
            contributors_as_maintainers = self.config.get(
                "contributors-as-maintainers", True
            )
            if not isinstance(contributors_as_maintainers, bool):
                raise TypeError(
                    "Option `contributors-as-maintainers` for metadata hook `{}` "
                    "must be a boolean".format(self.PLUGIN_NAME)
                )
            self.__contributors_as_maintainers = contributors_as_maintainers
        return self.__contributors_as_maintainers

    @property
    def homepage_label(self) -> bool:
        if self.__homepage_label is None:
            homepage_label = self.config.get("homepage-label", "Homepage")

            if not isinstance(homepage_label, str):
                raise TypeError(
                    "Option `homepage-label` for metadata hook `{}` "
                    "must be a string".format(self.PLUGIN_NAME)
                )
            self.__homepage_label = homepage_label
        return self.__homepage_label

    @property
    def bugs_label(self) -> bool:
        if self.__bugs_label is None:
            bug_tracker_label = self.config.get("bugs-label", "Bug Tracker")

            if not isinstance(bug_tracker_label, str):
                raise TypeError(
                    "Option `bugs-label` for metadata hook `{}` "
                    "must be a string".format(self.PLUGIN_NAME)
                )
            self.__bugs_label = bug_tracker_label
        return self.__bugs_label

    @property
    def repository_label(self) -> bool:
        if self.__repository_label is None:
            bug_tracker_label = self.config.get("repository-label", "Repository")

            if not isinstance(bug_tracker_label, str):
                raise TypeError(
                    "Option `repository-label` for metadata hook `{}` "
                    "must be a string".format(self.PLUGIN_NAME)
                )
            self.__repository_label = bug_tracker_label
        return self.__repository_label

    def load_package_data(self):
        path = os.path.normpath(os.path.join(self.root, self.path))
        if not os.path.isfile(path):
            raise OSError(f"file does not exist: {self.path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _parse_bugs(self, bugs: str | dict[str, str]) -> str | None:
        if isinstance(bugs, str):
            return bugs

        if "url" not in bugs:
            return None

        return bugs["url"]

    def _parse_person(self, person: dict[str, str]) -> dict[str, str]:
        result = {}
        if isinstance(person, dict):
            if {"url", "email"} & person.keys():
                result["name"] = person["name"]
                if "email" in person:
                    result["email"] = person["email"]
                return result
            else:
                author = person["name"]
        else:
            author = person
        match = re.match(AUTHOR_PATTERN, author)
        if match is None:
            raise ValueError(f"Invalid author name: {author}")
        name, email, _ = match.groups()
        result = {"name": name}
        if email is not None:
            result["email"] = email
        return result

    def _parse_repository(self, repository: str | dict[str, str]) -> str:
        if isinstance(repository, str):
            match = re.match(REPOSITORY_PATTERN, repository)
            if match is None:
                raise ValueError(f"Invalid repository string: {repository}")
            kind, identifier = match.groups()
            if kind is None:
                kind = "github"
            return urllib.parse.urljoin(REPOSITORY_TABLE[kind], identifier)

        return repository["url"]

    def update(self, metadata: dict[str, Any]):
        package = self.load_package_data()

        new_metadata = {"name": package["name"]}

        authors = None
        maintainers = None

        if "author" in package:
            authors = [self._parse_person(package["author"])]

        if "contributors" in package:
            contributors = [self._parse_person(p) for p in package["contributors"]]
            if self.contributors_as_maintainers:
                maintainers = contributors
            else:
                authors = [*(authors or []), *contributors]

        if authors is not None:
            new_metadata["authors"] = authors

        if maintainers is not None:
            new_metadata["maintainers"] = maintainers

        if "keywords" in package:
            new_metadata["keywords"] = package["keywords"]

        if "description" in package:
            new_metadata["description"] = package["description"]

        if "license" in package:
            new_metadata["license"] = package["license"]

        # Construct URLs
        urls = {}
        if "homepage" in package:
            urls[self.homepage_label] = package["homepage"]
        if "bugs" in package:
            bugs_url = self._parse_bugs(package["bugs"])
            if bugs_url is not None:
                urls[self.bugs_label] = bugs_url
        if "repository" in package:
            urls[self.repository_label] = self._parse_repository(package["repository"])

        # Write URLs
        if urls:
            new_metadata["urls"] = urls

        # Only use required metadata
        metadata.update(
            {
                k: v
                for k, v in new_metadata.items()
                if (self.fields is None or k in self.fields)
            }
        )
