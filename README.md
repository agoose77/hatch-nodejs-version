# hatch-nodejs-version

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-nodejs-version.svg)](https://pypi.org/project/hatch-nodejs-version)

-----
This provides a plugin for Hatch that uses a `package.json` file to determine (and update) project versions.

As the semver specification only specifies an addition prerelease segment (and build segment) to the release segment, this plugin restricts versions to these segments, i.e. `major.minor.patch-(pre)0`.  

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

### Version source options

| Option   | Type            | Default | Description                                                         |
|----------|-----------------|---------|---------------------------------------------------------------------|
| `fields` | `list` of `str` | None    | Optional list of fields to take from the generated metadata object. |

## License

`hatch-nodejs-version` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
