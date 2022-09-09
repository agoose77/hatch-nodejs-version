# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest

from hatch_nodejs_version.metadata_source import NodeJSMetadataHook


TRIVIAL_PYPROJECT_CONTENTS = """
[build-backend]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
[project]
name = "my-app"
version = "0.0.0"
[tool.hatch.metadata.hooks.nodejs]
"""

DEMO_PACKAGE_CONTENTS = """
{
  "name": "my-app",
  "version": "1.0.0",
  "description": "A terrible package",
  "keywords": [
    "what",
    "is",
    "the",
    "time"
  ],
  "homepage": "https://where-the-heart-is.com",
  "bugs": {
    "url": "https://www.send-help.com",
    "email": "funky@rider.com"
  },
  "license": "MIT",
  "author": {
    "name": "Alice Roberts",
    "email": "alice.roberts@bbc.lol"
  },
  "contributors": [
        {
        "name": "Isaac Newton",
        "email": "isaac.newton@apple.com"
      }
  ],
  "repository": {
    "type": "git",
    "url": "https://github.com/some/code.git"
  }
}
"""

EXPECTED_METADATA = {
    "license": "MIT",
    "urls": {
        "bug tracker": "https://www.send-help.com",
        "repository": "https://github.com/some/code.git",
        "homepage": "https://where-the-heart-is.com",
    },
    "authors": [
        {
            "name": "Alice Roberts",
            "email": "alice.roberts@bbc.lol",
        }
    ],
    "maintainers": [{"name": "Isaac Newton", "email": "isaac.newton@apple.com"}],
    "keywords": ["what", "is", "the", "time"],
    "description": "A terrible package",
    "name": "my-app",
}


class TestMetadata:
    @pytest.mark.parametrize(
        "alt_package_json",
        [None, "package-other.json"],
    )
    def test_all_metadata(self, project, alt_package_json):
        # Create a simple project
        package_json = "package.json" if alt_package_json is None else alt_package_json
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / package_json).write_text(DEMO_PACKAGE_CONTENTS)

        config = {} if alt_package_json is None else {"path": alt_package_json}
        metadata = {}
        metadata_source = NodeJSMetadataHook(project, config=config)
        metadata_source.update(metadata)

        assert metadata == EXPECTED_METADATA

    @pytest.mark.parametrize(
        "pyproject_field",
        [
            "urls",
            "description",
            "name",
            "keywords",
            "authors",
            "maintainers",
            "license",
        ],
    )
    def test_subset_metadata(self, project, pyproject_field):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(DEMO_PACKAGE_CONTENTS)

        config = {"fields": [pyproject_field]}

        metadata = {}
        metadata_source = NodeJSMetadataHook(project, config=config)
        metadata_source.update(metadata)

        assert pyproject_field in metadata
        assert len(metadata) == len(config["fields"])
        assert metadata[pyproject_field] == EXPECTED_METADATA[pyproject_field]

    def test_contributors_as_maintainers(self, project):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(DEMO_PACKAGE_CONTENTS)

        metadata = {}
        metadata_source = NodeJSMetadataHook(
            project, config={"contributors-as-maintainers": True}
        )
        metadata_source.update(metadata)

        assert metadata["authors"] == EXPECTED_METADATA["authors"]
        assert metadata["maintainers"] == EXPECTED_METADATA["maintainers"]

    def test_contributors_as_authors(self, project):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(DEMO_PACKAGE_CONTENTS)

        metadata = {}
        metadata_source = NodeJSMetadataHook(
            project, config={"contributors-as-maintainers": False}
        )
        metadata_source.update(metadata)

        assert (
            metadata["authors"]
            == EXPECTED_METADATA["authors"] + EXPECTED_METADATA["maintainers"]
        )
