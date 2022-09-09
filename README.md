# hatch-nodejs-version

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

-----
This provides a [version source plugin](https://hatch.pypa.io/latest/plugins/version-source/) for Hatch that reads/writes the package version from the `version` field of the NodeJS `package.json` file.


**Table of Contents**

- [Installation](#installation)
- [Global dependency](#global-dependency)
- [Version source](#version-source)
- [Metadata hook](#metadata-hook)
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
  
### Semver

The semver specification defines the following version sections:
- `major`
- `minor`
- `patch`
- `pre-release`
- `build`

Meanwhile, [PEP 440](https://peps.python.org/pep-0440/#version-scheme) defines:
- `epoch`
- `major`
- `minor`
- `patch`
- `pre-release`
- `post-release`
- `dev-release`

In order to ensure round-trip support, and ensure semantic consistency between NodeJS and Python, this plugin only accepts the common version parts:
- `major`
- `minor`
- `patch`
- `pre-release`

e.g. `1.2.3-rc0`.  

### Version source options

| Option        | Type | Default       | Description                                |
|---------------| --- |---------------|--------------------------------------------|
| `path`        | `str` | `package.json` | Relative path to the `package.json` file. |


## Metadata hook

The [metadata hook plugin](https://hatch.pypa.io/dev/plugins/metadata-hook/reference/) name is `nodejs`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.metadata.hooks.nodejs]
    ```

- ***hatch.toml***

    ```toml
    [metadata.hooks.nodejs]
    ```

### Metadata hook options

| Option   | Type            | Default | Description                                                         |
|----------|-----------------|---------|---------------------------------------------------------------------|
| `fields` | `list` of `str` | None    | Optional list of fields to take from the generated metadata object. |

## License

`hatch-nodejs-version` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
