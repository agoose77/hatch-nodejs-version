# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest

from hatch_nodejs_version.metadata_source import NodeJSMetadataHook


class TestMetadata:
    @pytest.mark.parametrize(
        "alt_package_json",
        [None, "package-other.json"],
    )
    @pytest.mark.parametrize(
        "pyproject_field",
        ["urls", "description", "name", "keywords", "author", "maintainers", "license"],
    )
    def test_metadata_from_package(self, project, alt_package_json, pyproject_field):
        # Create a simple project
        (project / "pyproject.toml").write_text(
            f"""
[build-backend]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
[project]
name = "my-app"
version = "0.0.0"
[tool.hatch.metadata.hooks.nodejs]
 """
        )
        package_json = "package.json" if alt_package_json is None else alt_package_json
        (project / package_json).write_text(
            """
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
        )
        config = {} if alt_package_json is None else {"path": alt_package_json}
        metadata_source = NodeJSMetadataHook(project, config=config)

        metadata = {}
        metadata_source.update(metadata)

        assert metadata["license"] == "MIT"
        assert metadata["urls"] == {
            "bug tracker": "https://www.send-help.com",
            "repository": "https://github.com/some/code.git",
            "homepage": "https://where-the-heart-is.com",
        }
        assert metadata["author"] == {
            "name": "Alice Roberts",
            "email": "alice.roberts@bbc.lol",
        }

        assert metadata["maintainers"] == [
            {"name": "Isaac Newton", "email": "isaac.newton@apple.com"}
        ]
        assert metadata["keywords"] == ["what", "is", "the", "time"]
        assert metadata["description"] == "A terrible package"
        assert metadata["name"] == "my-app"
