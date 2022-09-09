# SPDX-FileCopyrightText: 2022-present Angus Hollands <goosey15@gmail.com>
# SPDX-FileCopyrightText: 2022-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import errno
import os
import shutil
import stat
import tempfile
from contextlib import contextmanager
import pathlib

import pytest


def touch_file(path):
    with open(path, "a"):
        os.utime(path, None)


def create_file(path, contents):
    with open(path, "w") as f:
        f.write(contents)


@contextmanager
def create_project(directory):
    project_dir = directory / "my-app"
    os.mkdir(project_dir)

    package_dir = project_dir / "my_app"
    os.mkdir(package_dir)

    touch_file(package_dir / "__init__.py")
    touch_file(package_dir / "foo.py")
    touch_file(package_dir / "bar.py")
    touch_file(package_dir / "baz.py")

    origin = os.getcwd()
    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(origin)


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
        directory = pathlib.Path(os.path.realpath(directory))
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=False, onerror=handle_remove_readonly)


@pytest.fixture
def project(temp_dir):
    with create_project(temp_dir) as project:
        yield project
