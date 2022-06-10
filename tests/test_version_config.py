# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
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
]

BAD_NODE_VERSIONS = [
    "1.4",
    "1.4.5a0",
    "1.4.5-c0.post1",
    "1.4.5-rc0.post1.dev2",
]
BAD_PYTHON_VERSIONS = [
    "1.4",
    "1.4.5ab",
    "1.4.5-c0.smoke2",
    "1.4.5rc.post1@dev2",
]


class TestDefault:
    @pytest.mark.parametrize(
        "new_project, python_version", GOOD_NODE_PYTHON_VERSIONS, indirect=["new_project"]
    )
    @pytest.mark.parametrize("config", [{"path": "other-package.json"}, {}])
    def test_read_correct(self, new_project, python_version, config):
        version_source = NodeJSVersionSource(new_project, config)
        data = version_source.get_version_data()
        assert data["version"] == python_version

    @pytest.mark.parametrize("python_version,node_version", GOOD_NODE_PYTHON_VERSIONS)
    @pytest.mark.parametrize("config", [{"path": "other-package.json"}, {}])
    @pytest.mark.parametrize("new_project", ["1.0.0"], indirect=True)
    def test_write_correct(self, new_project, python_version, node_version, config):
        version_source = NodeJSVersionSource(new_project, config)
        data = version_source.get_version_data()
        version_source.set_version(python_version, data)
        data = version_source.get_version_data()
        assert data["version"] == node_version

    @pytest.mark.parametrize(
        "new_project",
        BAD_NODE_VERSIONS,
        indirect=["new_project"],
    )
    @pytest.mark.parametrize("config", [{"path": "other-package.json"}, {}])
    def test_read_incorrect(self, new_project, config):
        version_source = NodeJSVersionSource(new_project, config)

        with pytest.raises(ValueError, match=".* did not match regex"):
            version_source.get_version_data()

    @pytest.mark.parametrize("python_version,", BAD_PYTHON_VERSIONS)
    @pytest.mark.parametrize("new_project", ["1.0.0"], indirect=True)
    @pytest.mark.parametrize("config", [{"path": "other-package.json"}, {}])
    def test_write_incorrect(self, new_project, python_version, config):
        version_source = NodeJSVersionSource(new_project, config)
        data = version_source.get_version_data()
        with pytest.raises(ValueError, match=".* did not match regex"):
            version_source.set_version(python_version, data)
