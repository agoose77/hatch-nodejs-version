# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
import json

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

TRIVIAL_PACKAGE_CONTENTS = """
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

TRIVIAL_EXPECTED_METADATA = {
    "license": "MIT",
    "urls": {
        "Bug Tracker": "https://www.send-help.com",
        "Repository": "https://github.com/some/code.git",
        "Homepage": "https://where-the-heart-is.com",
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
        (project / package_json).write_text(TRIVIAL_PACKAGE_CONTENTS)

        config = {} if alt_package_json is None else {"path": alt_package_json}
        metadata = {}
        metadata_source = NodeJSMetadataHook(project, config=config)
        metadata_source.update(metadata)

        assert metadata == TRIVIAL_EXPECTED_METADATA

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
        (project / "package.json").write_text(TRIVIAL_PACKAGE_CONTENTS)

        config = {"fields": [pyproject_field]}

        metadata = {}
        metadata_source = NodeJSMetadataHook(project, config=config)
        metadata_source.update(metadata)

        assert pyproject_field in metadata
        assert len(metadata) == len(config["fields"])
        assert metadata[pyproject_field] == TRIVIAL_EXPECTED_METADATA[pyproject_field]

    def test_contributors_as_maintainers(self, project):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(TRIVIAL_PACKAGE_CONTENTS)

        metadata = {}
        metadata_source = NodeJSMetadataHook(
            project, config={"contributors-as-maintainers": True}
        )
        metadata_source.update(metadata)

        assert metadata["authors"] == TRIVIAL_EXPECTED_METADATA["authors"]
        assert metadata["maintainers"] == TRIVIAL_EXPECTED_METADATA["maintainers"]

    def test_contributors_as_authors(self, project):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(TRIVIAL_PACKAGE_CONTENTS)

        metadata = {}
        metadata_source = NodeJSMetadataHook(
            project, config={"contributors-as-maintainers": False}
        )
        metadata_source.update(metadata)

        assert (
            metadata["authors"]
            == TRIVIAL_EXPECTED_METADATA["authors"]
            + TRIVIAL_EXPECTED_METADATA["maintainers"]
        )

    def test_labels(self, project):
        # Create a simple project
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(TRIVIAL_PACKAGE_CONTENTS)

        metadata = {}
        metadata_source = NodeJSMetadataHook(
            project,
            config={
                "repository-label": "the-repository",
                "bugs-label": "the-bug-tracker",
                "homepage-label": "the-homepage",
            },
        )
        metadata_source.update(metadata)

        urls = metadata["urls"]
        assert urls["the-repository"] == "https://github.com/some/code.git"
        assert urls["the-bug-tracker"] == "https://www.send-help.com"
        assert urls["the-homepage"] == "https://where-the-heart-is.com"

    def test_authors_accepted_as_strings(self, project):
        original_package_content = json.loads(TRIVIAL_PACKAGE_CONTENTS)
        updated_package_content = original_package_content.copy()
        author_as_string = f"{original_package_content['author']['name']} " \
                           f"<{original_package_content['author']['email']}>"
        updated_package_content['author'] = author_as_string
        (project / "pyproject.toml").write_text(TRIVIAL_PYPROJECT_CONTENTS)
        (project / "package.json").write_text(json.dumps(updated_package_content))

        config = {}
        metadata = {}
        metadata_source = NodeJSMetadataHook(project, config=config)
        metadata_source.update(metadata)
        assert metadata == TRIVIAL_EXPECTED_METADATA

