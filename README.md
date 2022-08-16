# OCL (OpenShift Login)

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]


OCL does an automatic login to an OpenShift cluster. It fetches cluster information from app-interface and performs a login via [Selenium](https://selenium-python.readthedocs.io).

## Installation

You can install this library from [PyPI](https://pypi.org/project/pyworkon/) with `pip`:


```shell
$ python3 -m pip install ocl
```

or install it with `pipx`:
```shell
$ pipx install ocl
```

You can also use `pipx` to run the library without installing it:

```shell
$ pipx run ocl
```

## Features

OCL currently provides the following features (get help with `-h` or `--help`):

- OpenShift console login (oc login) via GitHub authentication
- Get cluster information from app-interface or user defined (`OCL_USER_CLUSTERS`)
- Open OpenShift console in browser (`--open-in-browser`)
- Shell completion (`--install-completion`, `--show-completion`)
- Credentials via environment variables or shell command (e.g. [1password CLI](https://developer.1password.com/docs/cli/))


## Enviroment Variables


## Limitations

* MacOS only
* Only Selenium `webdriver.Chrome` is supported and must be installed manually
  ```shell
  $ brew install --cask chromedriver
  ```


## Development

[![pre-commit.ci status][pre-commit-badge]][pre-commit-link]
[![Code style: black][black-badge]][black-link]


[black-badge]:              https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]:               https://github.com/psf/black
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/pyworkon
[conda-link]:               https://github.com/conda-forge/pyworkon-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/chassing/pyworkon/discussions
[pypi-link]:                https://pypi.org/project/pyworkon/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/pyworkon
[pypi-version]:             https://badge.fury.io/py/pyworkon.svg
