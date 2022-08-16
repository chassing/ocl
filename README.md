# OCL (OpenShift Login)

[![PyPI](https://img.shields.io/pypi/v/openshift-cluster-login)][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
![PyPI - License](https://img.shields.io/pypi/l/openshift-cluster-login)

OCL does an automatic login to an OpenShift cluster. It fetches cluster information from app-interface and performs a login via [Selenium](https://selenium-python.readthedocs.io).

## Installation

You can install this library from [PyPI][pypi-link] with `pip`:


```shell
$ python3 -m pip install openshift-cluster-login
```

or install it with `pipx`:
```shell
$ pipx install openshift-cluster-login
```

You can also use `pipx` to run the library without installing it:

```shell
$ pipx run openshift-cluster-login
```

## Usage

```shell
$ ocl
```
## Features

OCL currently provides the following features (get help with `-h` or `--help`):

- OpenShift console login (oc login) via GitHub authentication
- Get cluster information from app-interface or user defined (`OCL_USER_CLUSTERS`)
- Open OpenShift console in browser (`--open-in-browser`)
- Shell completion (`--install-completion`, `--show-completion`)
- Credentials via environment variables or shell command (e.g. [1password CLI](https://developer.1password.com/docs/cli/))


## Enviroment Variables

| Variable Name                 | Description                                                                                                                  | Default |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------- |
| OCL_GITHUB_USERNAME           | Your GitHub username                                                                                                         |         |
| OCL_GITHUB_USERNAME_COMMAND   | Command to retrieve your GitHub username                                                                                     |         |
| OCL_GITHUB_PASSWORD           | Your GitHub password                                                                                                         |         |
| OCL_GITHUB_PASSWORD_COMMAND   | Command to retrieve your GitHub password  (e.g. `op read op://Private/Github/password`)                                      |         |
| OCL_GITHUB_TOTP               | Your GitHub two factor token                                                                                                 |         |
| OCL_GITHUB_TOTP_COMMAND       | Command to retrieve your GitHub two factor token (e.g. `op item get Github --otp`)                                           |         |
| OCL_WAIT                      | Selenium webdriver wait timeout                                                                                              | 2       |
| OCL_WAIT_COMMAND              | Command to retrieve Selenium webdriver wait timeout                                                                          |         |
| OCL_APP_INTERFACE_URL         | App-Interface URL                                                                                                            |         |
| OCL_APP_INTERFACE_URL_COMMAND | Command to retrieve App-Interface URL                                                                                        |         |
| OCL_APP_INT_TOKEN             | App-Interface authentication token                                                                                           |         |
| OCL_APP_INT_TOKEN_COMMAND     | Command to retrieve App-Interface authentication token                                                                       |         |
| USER_CLUSTERS                 | User defined clusters (e.g. `[{"name": "local-kind", "serverUrl": "https://localhost:6443", "consoleUrl": "not available}]`) |         |
| USER_CLUSTERS_COMMAND         | Command to retrieve User defined clusters                                                                                    |         |

## Limitations

* MacOS only
* Only Selenium `webdriver.Chrome` is supported and must be installed manually
  ```shell
  $ brew install --cask chromedriver
  ```


## Development

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)


[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/chassing/ocl/discussions
[pypi-link]:                https://pypi.org/project/openshift-cluster-login/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/openshift-cluster-login
[pypi-version]:             https://badge.fury.io/py/openshift-cluster-login.svg
