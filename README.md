![logo](images/logo-white-bg.png)
# OCL (OpenShift Login)

[![PyPI](https://img.shields.io/pypi/v/openshift-cluster-login)][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
![PyPI - License](https://img.shields.io/pypi/l/openshift-cluster-login)
[![Release and Package Application](https://github.com/chassing/ocl/actions/workflows/release.yaml/badge.svg)](https://github.com/chassing/ocl/actions/workflows/release.yaml)

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

<img src="demo/quickstart.gif"/>

This spawns a new shell with the following environment variables are set:

* `KUBECONFIG` - path to kubeconfig file
* `OCL_CLUSTER_NAME` - cluster name
* `OCL_CLUSTER_CONSOLE` - url to cluster console

## Features

OCL currently provides the following features (get help with `-h` or `--help`):

- OpenShift console login (`oc login`) via GitHub or Red Hat authentication
- Get cluster information from app-interface or user-defined (`OCL_USER_CLUSTERS``)
_ Open the OpenShift `console in `the `browser`` (`--open-in-browser`)
- Shell completion (`--install-completion`, `--show-completion`)
- Credentials via environment variables or shell command (e.g., [1password CLI](https://developer.1password.com/docs/cli/))
- Cache App-Interface queries (via GraphQL) for one week


## Environment Variables

| Variable Name                                       | Description                                                                                                                                 | Default |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| OCL_GITHUB_USERNAME OCL_GITHUB_USERNAME_COMMAND     | Your GitHub username                                                                                                                        |         |
| OCL_GITHUB_PASSWORD OCL_GITHUB_PASSWORD_COMMAND     | Your GitHub password (e.g. command `op read op://Private/Github/password`)                                                                  |         |
| OCL_GITHUB_TOTP OCL_GITHUB_TOTP_COMMAND             | Your GitHub two factor token (e.g. command `op item get Github --otp`)                                                                      |         |
| OCL_RH_USERNAME OCL_RH_USERNAME_COMMAND             | Your Red Hat username                                                                                                                       |         |
| OCL_RH_PASSWORD OCL_RH_PASSWORD_COMMAND             | Your Red Hat password (e.g. command `op read op://Private/RH/password`)                                                                     |         |
| OCL_RH_TOTP OCL_RH_TOTP_COMMAND                     | Your Red Hat two factor token (e.g. command `op item get RH --otp`)                                                                         |         |
| OCL_WAIT OCL_WAIT_COMMAND                           | Selenium webdriver wait timeout                                                                                                             | 2       |
| OCL_APP_INTERFACE_URL OCL_APP_INTERFACE_URL_COMMAND | App-Interface URL                                                                                                                           |         |
| OCL_APP_INT_TOKEN OCL_APP_INT_TOKEN_COMMAND         | App-Interface authentication token                                                                                                          |         |
| USER_CLUSTERS USER_CLUSTERS_COMMAND                 | User defined clusters as json format (e.g. `[{"name": "local-kind", "serverUrl": "https://localhost:6443", "consoleUrl": "not available}]`) | "[]"    |

You can either set a variable, e.g. `export OCL_GITHUB_USERNAME="mail@example.com"` or retrieve it via a command, e.g. `export OCL_GITHUB_USERNAME_COMMAND="op read op://Private/Github/username"`.
If a variable is not set but needed, OCL will ask for it interactively.

## App-Interface

OCL retrieves the cluster information from app-interface via GraphQL (`OCL_APP_INTERFACE_URL`) and caches them
in your user *cache directory* (on MacOS, e.g., `~/Library/Caches/ocl/gql_cache/`).
Remove this directory to force a refresh.

## Limitations

* MacOS only
* Only Selenium `webdriver.Chrome` is supported and must be installed manually
  ```shell
  $ brew install --cask chromedriver
  ```


## Development

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)


Use [Conventional Commit messages](https://www.conventionalcommits.org).
The most important prefixes you should have in mind are:

* `fix:` which represents bug fixes, and correlates to a [SemVer](https://semver.org/)
  patch.
* `feat:` which represents a new feature, and correlates to a SemVer minor.
* `feat!:`,  or `fix!:`, `refactor!:`, etc., which represent a breaking change
  (indicated by the `!`) and will result in a SemVer major.
* `chore: release` to create a new release

Consider using an empty commit:

```
git commit --allow-empty -m "chore: release"
```

When a commit to the main branch has `Release-As: x.x.x` (case insensitive) in the **commit body**, Release Please will open a new pull request for the specified version.
```
git commit --allow-empty -m "chore: release 2.0.0" -m "Release-As: 2.0.0"
```


[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/chassing/ocl/discussions
[pypi-link]:                https://pypi.org/project/openshift-cluster-login/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/openshift-cluster-login
[pypi-version]:             https://badge.fury.io/py/openshift-cluster-login.svg
