# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) when possible.

## [1.1.2] - 2025-03-18

### Added

- Full support for python versions 3.8 - 3.13.
- Added state_name to the `__init_subclass__` of State.

### Removed

- Removed `State.clock` (The pygame clock).

## [1.1.1] - 2025-03-17

### Fixed

- Fixed docstrings of classes & methods

### Changed

- Changed `__states`, `__current_state` and `__last_state` to `_states`, `_current_state`, `_last_state` respectively, in the `StateManager`.
- Changed the docstyle from numpy to sphinx style.
