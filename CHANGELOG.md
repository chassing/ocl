# Changelog

## 1.2.0

* Use [uv](https://docs.astral.sh/uv/) package manager
* Upgrade dependencies

## 1.1.1

* New `--quiet` option to suppress output

## 1.1.0

* Abandon GitHub releases in favor of PyPI
* Upgrade dependencies

## 1.0.6

* New `--command` option to run a single command and exit

## 1.0.5

* `OCL_CACHE_TIMEOUT_MINUTES` GraphQL cache timeout is now configurable; default is 1 hour

## 1.0.4

* auto-completion support for cluster and project names

## 1.0.3

* `OCL_APP_INT_TOKEN` is now optional

## 1.0.2

### Features

* ROSA HyperShift cluster support

## 1.0.1

### Bug Fixes

* fix namespace selector for namespaces with the same name on different clusters

## [1.0.0](https://github.com/chassing/ocl/compare/v0.12.4...v1.0.0) (2024-01-08)

### ⚠ BREAKING CHANGES

* select namespaces instead of clusters
* replace selenium oauth dance with Kerberos auth

### Features

* replace selenium oauth dance with Kerberos auth ([cd2f2d1](https://github.com/chassing/ocl/commit/cd2f2d10dd7e2ade5bd1e8c1581d587cd202e6d3))
* select namespaces instead of clusters ([eb6c7e1](https://github.com/chassing/ocl/commit/eb6c7e11fc90d07bfc824fdacca232d6c11dfdaa))

## [0.12.4](https://github.com/chassing/ocl/compare/v0.12.3...v0.12.4) (2023-02-17)

### Bug Fixes

* **redhat-idp:** support staging redhat SSO instance ([95ab055](https://github.com/chassing/ocl/commit/95ab055541d2bb0f6e888523ab96f0ca58c8a44a))

## [0.12.3](https://github.com/chassing/ocl/compare/v0.12.2...v0.12.3) (2023-02-14)

### Bug Fixes

* **chromedriver:** fix headless mode ([8ff2ae6](https://github.com/chassing/ocl/commit/8ff2ae607d2abc7dca70a49171dc4c5890dd134b))

## [0.12.2](https://github.com/chassing/ocl/compare/v0.12.1...v0.12.2) (2023-02-07)

### Bug Fixes

* **github:** fix TOTP input field selector ([32e6958](https://github.com/chassing/ocl/commit/32e6958fac568acb12ce2b5342c785529d905976))

## [0.12.1](https://github.com/chassing/ocl/compare/v0.12.0...v0.12.1) (2023-01-24)

### Bug Fixes

* **env vars:** fix getting environment variables ([6d4d5a3](https://github.com/chassing/ocl/commit/6d4d5a3d705024381778907952f392fd03572019))

## [0.12.0](https://github.com/chassing/ocl/compare/v0.11.0...v0.12.0) (2023-01-17)

### Features

* ask for missing env variables interactively ([fc0c534](https://github.com/chassing/ocl/commit/fc0c5345a51c4af0edcf039eec07b9f5794f4c67))

## [0.11.0](https://github.com/chassing/ocl/compare/v0.10.1...v0.11.0) (2023-01-11)

### Features

* automatic IDP detection ([a24ffb7](https://github.com/chassing/ocl/commit/a24ffb7fb1f3ae2022980b5a3d9b6c0eb4ae3be4))

## [0.10.1](https://github.com/chassing/ocl/compare/v0.10.0...v0.10.1) (2022-12-21)

### Bug Fixes

* **browser:** more robust wait for login pages ([14d13af](https://github.com/chassing/ocl/commit/14d13af166d7354e4fefeebe23689c7251d0e207))

## [0.10.0](https://github.com/chassing/ocl/compare/v0.9.0...v0.10.0) (2022-12-21)

### Features

* **idp:** Red Hat SSO IDP support ([c35fceb](https://github.com/chassing/ocl/commit/c35fcebd11e44918926b3d953b3c84bddfab5adf))

### Bug Fixes

* **browser:** improve performance; no more implicit waits ([a1c01a0](https://github.com/chassing/ocl/commit/a1c01a0133cb0aeb0e542a76e1552ea77dfa45ee))
* **deps:** update dependencies ([69b79e2](https://github.com/chassing/ocl/commit/69b79e2ae2feddf8faba4c8ce229d7e89b5de2c5))

## [0.9.0](https://github.com/chassing/ocl/compare/v0.8.1...v0.9.0) (2022-12-21)

### Features

* --idp option to support manual logins ([be3560f](https://github.com/chassing/ocl/commit/be3560f0c01cb239d95d9dc34d6b32c048392b8d))

## [0.8.1](https://github.com/chassing/ocl/compare/v0.8.0...v0.8.1) (2022-11-28)

### Bug Fixes

* adapt cluster GQL changes ([070c168](https://github.com/chassing/ocl/commit/070c1687b63e026b4aa35539a2605f3466b1819d))

## [0.8.0](https://github.com/chassing/ocl/compare/v0.7.0...v0.8.0) (2022-11-08)

### Features

* **app-interface:** cache app-interface cluster query result for one week ([44f002e](https://github.com/chassing/ocl/commit/44f002e284512af6c87968376a236882ecb2167a))

## [0.7.0](https://github.com/chassing/ocl/compare/v0.6.0...v0.7.0) (2022-11-07)

### Features

* **open-in-browser:** "." to reference OCL_CLUSTER_NAME ([3ea2a0e](https://github.com/chassing/ocl/commit/3ea2a0eefeab52bc207583606af695cf6497b416))

## [0.6.0](https://github.com/chassing/ocl/compare/v0.5.1...v0.6.0) (2022-09-21)

### Features

* --refresh-login cli option to enforce a new token ([4dd2a45](https://github.com/chassing/ocl/commit/4dd2a451e2adc8e28d1457cd32ce571f60f73cdc))

### Bug Fixes

* add file lock to handle running ocl concurrently ([9905a94](https://github.com/chassing/ocl/commit/9905a9443bb184134c28abd755870ac2a58cf45f))
* document cli options (--help) ([7c65e50](https://github.com/chassing/ocl/commit/7c65e5090ba91eebb3bd096bd61eac140a552af3))

## [0.5.1](https://github.com/chassing/ocl/compare/v0.5.0...v0.5.1) (2022-09-19)

### Bug Fixes

* **k8s:** use cluster-info instead whoami to check access ([edfa679](https://github.com/chassing/ocl/commit/edfa67956a4c3ce96716cffbbe77908cd8d974c1))

## [0.5.0](https://github.com/chassing/ocl/compare/v0.4.2...v0.5.0) (2022-09-16)

### Features

* use temp KUBECONFIG file for each new ocl shell ([b58b411](https://github.com/chassing/ocl/commit/b58b41198c22d512bb72b6f71059b838d2efa6e5))

## [0.4.2](https://github.com/chassing/ocl/compare/v0.4.1...v0.4.2) (2022-09-06)

### Bug Fixes

* **chore:** typo ([2233251](https://github.com/chassing/ocl/commit/2233251436768537e504837eec786204bbd02319))

## [0.4.1](https://github.com/chassing/ocl/compare/v0.4.0...v0.4.1) (2022-09-06)

### Bug Fixes

* **openshift:** display url for open-in-browser ([543eff5](https://github.com/chassing/ocl/commit/543eff558713420056c38caa8cc92579976ed84f))

## [0.4.0](https://github.com/chassing/ocl/compare/v0.3.1...v0.4.0) (2022-09-06)

### Features

* **doc:** document shell env vars ([341ffae](https://github.com/chassing/ocl/commit/341ffae74933f8e016b4786c7d20e2d53ff5dc29))
* **shell:** set OCL_CLUSTER_CONSOLE with console url ([2f617ca](https://github.com/chassing/ocl/commit/2f617ca90b99af2467f65f7b2d9fe0aaff4737d6))

## [0.3.1](https://github.com/chassing/ocl/compare/v0.3.0...v0.3.1) (2022-08-31)

### Documentation

* update logo ([e866a64](https://github.com/chassing/ocl/commit/e866a64cd0d9f8afdcce7af1eb3fb8c653f291de))

## [0.3.0](https://github.com/chassing/ocl/compare/v0.2.0...v0.3.0) (2022-08-31)

### Features

* **openshift:** open in browser will enter project if given ([131828a](https://github.com/chassing/ocl/commit/131828a71bc890156efdb0c8cfe69a5704b75c62))

### Documentation

* add logo ([c0ac785](https://github.com/chassing/ocl/commit/c0ac78527b1849598710f035e981bdeed01027a6))

## [0.2.0](https://github.com/chassing/ocl/compare/v0.1.5...v0.2.0) (2022-08-30)

### Features

* **openshift:** enter project via CLI argument ([ed61a21](https://github.com/chassing/ocl/commit/ed61a2151062de03fae1fa7203666e14e68510d3))

## [0.1.5](https://github.com/chassing/ocl/compare/v0.1.4...v0.1.5) (2022-08-29)

### Bug Fixes

* **github:** handle github authorize page ([96a06c5](https://github.com/chassing/ocl/commit/96a06c5db033bd6c1eac87752747281f13c37133))

## [0.1.4](https://github.com/chassing/ocl/compare/v0.1.3...v0.1.4) (2022-08-18)

### Bug Fixes

* typo in oc_setup method ([796b3f7](https://github.com/chassing/ocl/commit/796b3f7e3887ebdf65580ac7c629fc405cabd67a))

### Documentation

* fix typos and workflow badge ([a8dd85e](https://github.com/chassing/ocl/commit/a8dd85e02f6486cb9d93cfe05fb28c99d958d1de))

## [0.1.3](https://github.com/chassing/ocl/compare/v0.1.2...v0.1.3) (2022-08-17)

### Bug Fixes

* make OCL_USER_CLUSTERS optional ([1504d55](https://github.com/chassing/ocl/commit/1504d55f8312af0e27644c119d986fb0f4b7d4aa))

### Documentation

* VAR vs VAR_COMMAND example ([ec6f0cd](https://github.com/chassing/ocl/commit/ec6f0cdbec99bc872baca76286c399bc0043836a))

## [0.1.2](https://github.com/chassing/ocl/compare/v0.1.1...v0.1.2) (2022-08-16)

### Bug Fixes

* type hint style for python 3.9 ([7164e7e](https://github.com/chassing/ocl/commit/7164e7e67c931d2136136b1b0380f6e4c53b49a6))

## [0.1.1](https://github.com/chassing/ocl/compare/v0.1.0...v0.1.1) (2022-08-16)

### Bug Fixes

* **gh-action:** use latest ubuntu to build pypi packages ([6b5e4f4](https://github.com/chassing/ocl/commit/6b5e4f41372978cf154a0881f3a0ad200e806709))

## 0.1.0 (2022-08-16)

### ⚠ BREAKING CHANGES

* PyPI release

### Features

* PyPI release ([aa2a097](https://github.com/chassing/ocl/commit/aa2a097146a20bc49a087b0271d0cd152f4992f8))

### Bug Fixes

* **gh-action:** main is the name of the branch ([069f702](https://github.com/chassing/ocl/commit/069f70291b147a2ac3563b7606e4e6971bd417f1))
