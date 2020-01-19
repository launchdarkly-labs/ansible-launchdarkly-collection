Change log
================================================

All notable changes to the LaunchDarkly Ansible Collection will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org).

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
