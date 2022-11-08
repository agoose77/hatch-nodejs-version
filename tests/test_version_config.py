# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path

import pytest

from hatch_nodejs_version.version_source import NodeJSVersionSource

GOOD_NODE_PYTHON_VERSIONS = [
    ("1.4.5", "1.4.5"),
    ("1.4.5-a0", "1.4.5a0"),
    ("1.4.5-a", "1.4.5a"),
    ("1.4.5-b0", "1.4.5b0"),
    ("1.4.5-c1", "1.4.5c1"),
    ("1.4.5-rc0", "1.4.5rc0"),
    ("1.4.5-alpha0", "1.4.5alpha0"),
    ("1.4.5-beta0", "1.4.5beta0"),
    ("1.4.5-pre9", "1.4.5pre9"),
    ("1.4.5-preview0", "1.4.5preview0"),
    ("1.4.5-preview0+build1.0.0", "1.4.5preview0+build1.0.0"),
    ("1.4.5-preview0+build-1.0.0", "1.4.5preview0+build-1.0.0"),
    ("1.4.5-preview0+good-1_0.0", "1.4.5preview0+good-1_0.0"),
]


class TestVersion:
    @pytest.mark.parametrize(
        "python_version",
        [
            "1.4",
            "1.4.5ab",
            "1.4.5-c0.smoke2",
            "1.4.5rc.post1@dev2",
            "1.4.5rc0.post1+-bad",
            "1.4.5rc0.post1+bad_",
        ],
    )
    def test_parse_python_incorrect(self, python_version):
        with pytest.raises(ValueError, match=".* did not match regex"):
            NodeJSVersionSource.python_version_to_node(python_version)

    @pytest.mark.parametrize(
        "node_version",
        [
            "1.4",
            "1.4.5a0",
            "1.4.5-c0.post1",
            "1.4.5-rc0.post1.dev2",
            "1.4.5-rc0.post1+-bad",
            "1.4.5-rc0.post1+bad_",
        ],
    )
    def test_parse_node_incorrect(self, node_version):
        with pytest.raises(ValueError, match=".* did not match regex"):
            NodeJSVersionSource.node_version_to_python(node_version)

    @pytest.mark.parametrize(
        "node_version, python_version",
        GOOD_NODE_PYTHON_VERSIONS,
    )
    @pytest.mark.parametrize(
        "alt_package_json",
        [None, "package-other.json"],
    )
    def test_version_from_package(
        self, project, node_version, python_version, alt_package_json
    ):
        # Create a simple project
        (project / "pyproject.toml").write_text(
            """
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
[project]
name = "my-app"
dynamic = ["version"]
[tool.hatch.version]
source = "nodejs"
 """
        )
        package_json = "package.json" if alt_package_json is None else alt_package_json
        (project / package_json).write_text(
            f"""
{{
  "name": "my-app",
  "version": "{node_version}"
}}
"""
        )
        config = {} if alt_package_json is None else {"path": alt_package_json}
        version_source = NodeJSVersionSource(project, config=config)
        data = version_source.get_version_data()
        assert data["version"] == python_version

    @pytest.mark.parametrize(
        "node_version, python_version",
        GOOD_NODE_PYTHON_VERSIONS,
    )
    @pytest.mark.parametrize(
        "alt_package_json",
        [None, "package-other.json"],
    )
    def test_version_to_package(
        self, project, node_version, python_version, alt_package_json
    ):
        package_json = "package.json" if alt_package_json is None else alt_package_json
        (project / "pyproject.toml").write_text(
            """
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
[project]
name = "my-app"
dynamic = ["version"]
[tool.hatch.version]
source = "nodejs"
 """
        )
        (project / package_json).write_text(
            """
{
  "name": "my-app",
  "version": "0.0.0"
}
"""
        )
        config = {} if alt_package_json is None else {"path": alt_package_json}
        version_source = NodeJSVersionSource(project, config=config)
        version_data = version_source.get_version_data()
        version_source.set_version(python_version, version_data)

        written_package = json.loads((project / package_json).read_text())
        assert written_package["version"] == node_version

    @pytest.mark.parametrize(
        "node_version, python_version",
        GOOD_NODE_PYTHON_VERSIONS,
    )
    @pytest.mark.parametrize("version_file", [None, "my_app/_version.py"])
    @pytest.mark.parametrize(
        "template, version_var, expected_version",
        [
            [None, "__version__", lambda v: v],
            [
                """version = tuple("{version!s}".split("."))\n""",
                "version",
                lambda v: tuple(v.split(".")),
            ],
        ],
    )
    def test_python_version_file(
        self,
        project,
        node_version,
        python_version,
        version_file,
        template,
        version_var,
        expected_version,
    ):
        package_json = "package.json"
        (project / "pyproject.toml").write_text(
            """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "my-app"
dynamic = ["version"]
[tool.hatch.version]
source = "nodejs"
 """
        )
        (project / package_json).write_text(
            """
{
  "name": "my-app",
  "version": "0.0.0"
}
"""
        )
        config = {}
        if version_file is not None:
            config["version-file"] = version_file
        if template is not None:
            config["template"] = template
        version_source = NodeJSVersionSource(project, config=config)
        version_data = version_source.get_version_data()
        current_content = set((project / "my_app").iterdir())
        version_source.set_version(python_version, version_data)

        if version_file is None:
            # Check no new file was created
            assert len(current_content.difference((project / "my_app").iterdir())) == 0
        else:
            python_code = (project / version_file).read_text()
            local_vars = {}
            exec(python_code, {}, local_vars)

            assert local_vars[version_var] == expected_version(python_version)
