# hatch-nodejs-version

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Global dependency

Ensure `hatch-nodejs-version` is defined within the `build-system.requires` field in your `pyproject.toml` file.

```toml
[build-system]
requires = ["hatchling", "hatch-nodejs-version"]
build-backend = "hatchling.build"
```

## Version source

The [version source plugin](https://hatch.pypa.io/latest/plugins/version-source/) name is `nodejs`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    source = "nodejs"
    ```

- ***hatch.toml***

    ```toml
    [version]
    source = "nodejs"
    ```

### Version source options

| Option        | Type | Default       | Description                                |
|---------------| --- |---------------|--------------------------------------------|
| `path`        | `str` | `package.json` | Relative path to the `package.json` file. |

## License

`hatch-nodejs-version` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
