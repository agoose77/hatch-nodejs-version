# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
# SPDX-FileCopyrightText: 2022-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
from contextlib import contextmanager
from pathlib import Path

import pytest


def touch_file(path):
    with open(path, "a"):
        os.utime(path, None)


def create_file(path, contents):
    with open(path, "w") as f:
        f.write(contents)


@contextmanager
def create_project(directory: Path):
    project_dir = directory / "my-app"
    project_dir.mkdir()

    package_dir = project_dir / "my_app"
    package_dir.mkdir()

    (package_dir / "__init__.py").touch()
    (package_dir / "foo.py").touch()
    (package_dir / "bar.py").touch()
    (package_dir / "baz.py").touch()

    origin = os.getcwd()
    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(origin)


@pytest.fixture
def project(tmp_path):
    with create_project(tmp_path) as project:
        yield project
