# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
# SPDX-FileCopyrightText: 2022-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import errno
import shutil
import stat
import tempfile
from contextlib import contextmanager
import os
import pytest


def touch_file(path):
    with open(path, "a"):
        os.utime(path, None)


def create_file(path, contents):
    with open(path, "w") as f:
        f.write(contents)


def handle_remove_readonly(func, path, exc):  # no cov
    # PermissionError: [WinError 5] Access is denied: '...\\.git\\...'
    if func in (os.rmdir, os.remove, os.unlink) and exc[1].errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        func(path)
    else:
        raise


@pytest.fixture
def temp_dir():
    directory = tempfile.mkdtemp()
    try:
        directory = os.path.realpath(directory)
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=False, onerror=handle_remove_readonly)


@contextmanager
def create_project(directory, metadata, version):
    project_dir = os.path.join(directory, "my-app")
    os.mkdir(project_dir)

    project_file = os.path.join(project_dir, "pyproject.toml")
    create_file(project_file, metadata)

    package_dir = os.path.join(project_dir, "my_app")
    os.mkdir(package_dir)

    package_file = os.path.join(project_dir, "package.json")
    package = f"""
{{
  "name": "my-awesome-package",
  "version": "{version}"
}}
    """
    create_file(package_file, package)

    other_package_file = os.path.join(project_dir, "other-package.json")
    create_file(other_package_file, package)

    touch_file(os.path.join(package_dir, "__init__.py"))
    touch_file(os.path.join(package_dir, "foo.py"))
    touch_file(os.path.join(package_dir, "bar.py"))
    touch_file(os.path.join(package_dir, "baz.py"))

    origin = os.getcwd()
    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(origin)


@pytest.fixture
def new_project(temp_dir, request):
    with create_project(
        temp_dir,
        """\
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
[project]
name = "my-app"
dynamic = ["version"]
[tool.hatch.version]
source = "nodejs"
""",
        request.param,
    ) as project:
        yield project
