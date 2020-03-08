Change log
================================================

All notable changes to the LaunchDarkly Ansible Collection will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org).

## [0.2.9] - 2020-03-08
### Fixed:
- core: add missing launchdarkly_feature_flag_info file

### Added:
- core: rate limiting check for feature_flag_info

## [0.2.7] - 2020-03-07
### Fixed:
- core: flag variation bug if updating flag
- core: flag sync to correctly use included and excluded actions

## [0.2.6] - 2020-02-20
## Added:
- core: Use notresources and notactions in policies

## [0.2.5] - 2020-02-03
### Fixed:
- core: flag environment targeting bug
- core: fix ability to add/remove individual targets instead of just replacing

### Added:
- test: more coverage of flag targeting rules

## [0.2.4] - 2020-01-19
### Fixed:
- core: Some ApiExceptions were not causing modules to fail
- test: fixed user segment test
- test: allow tests to be run locally and in pipeline

### Added:
- meta: implement integration tests in pipeline
- meta: implement black linter

## [0.2.1] - 2019-12-30
### Fixed:
- core: properly return error messages
- core: try/catch on rollout key not existing

## [0.2.0] - 2019-12-04
### Fixed:
- core: lookup includes now import dependencies properly
- test: fix webhook return variable
- test: add coverage for new modules

### Added:
- core: Add multiple modules: launchdarkly_variation_info, launchdarkly_test_generator
- meta: run black against all python files
- docs: move API key to fragment

## [0.1.15] - 2019-11-21
### Fixed:
- core: Feature Flag Environment to dictionary
- core: Feature Flag Sync
- core: Fix import path for rule, with new namespace

### Added:
- Test coverage for Feature Flag Sync
- Docs: add more return docs

### Removed:
- Docs: Remove unused index on docs page

## [0.1.1] - 2019-11-17
### Fixed:
- Fix import path for new `launchdarkly_labs` namespace.
