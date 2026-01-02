# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) when possible.

## [2.4.0] - 2026-01-02

### Added

- `game_state.AsyncStateManager`.
- `game_state.AsyncState`.

### Fixed

- Fixed documentation for `StateManager` & `State`.

### Changed

- Updated test cases to improve coverage.

### Removed

- `window` parameter in `StateManager`'s `__init__`.
- `StateManager.global_on_setup` property.
- `State.window` attribute.
- `State.on_setup`.
- `State.process_event`.
- `State.process_update`.

## [2.3.1] - 2025-12-31

### Fixed

- Fixed docstring of `StateManager.remove_lazy_state`.

### Deprecated

- Deprecated `State.process_event` & `State.process_update`.

## [2.3.0] - 2025-12-19

### Added

- `State.on_load` method.
- `State.on_unload` method.
- Added overloads for `State.__init_subclass__` method.

### Fixed

- Fixed a typo in `State.on_enter` parameter.

### Changed

- `State` and `StateManager` are generics now for extended typing support.
- Updated guides to move away from the deprecations.
- Changed the type of `event` in `State.process_event` from `pygame.Event` to `typing.Any`.

### Deprecated

- All the following deprecations are staged for removal in version `2.4.0`.
- `window` parameter in `StateManager`'s `__init__` is deprecated and staged for removal.
- `StateManager.global_on_setup` is deprecated and staged for removal.
- `State.window` is deprecated and staged for removal.
- `State.global_on_setup` is deprecated and staged for removal.

## [2.2.0] - 2025-12-10

### Added

- Added auto state loading.
- Added `eager_load` & `lazy_lazy` load parameters to `State.__init_subclass__`.
- Added documentation for `State.__init_subclass__`.
- Added guides for lazy, eager loading and state args.
- `StateManager.lazy_state_map` property.
- `StateManager.add_lazy_states` method.
- `StateManager.remove_lazy_state` method.

### Fixed

- Fixed many documentation errors.

## [2.1.0] - 2025-11-04

### Added

- Added `game_state.utils.StateArgs`.
- Added documentation for `game_state.utils` module.
- Added examples on `game_state.utils.StateArgs` and it's usage.

### Fixed

- Fixed loading arguments to specific states in `game_state.StateManager.load_states`.

## [2.0.3] - 2025-10-20

### Added

- Added support to python version 3.14.
- Added Code of Conduct.
- Added CONTRIBUTING guidelines.

### Changed

- Updated author name throughout the project.
- Documentation guide now covers how to use state hooks.
- Examples & guide use better naming standards.
- Global listeners can now accept `NoneType`.

## [2.0.2] - 2025-09-23

### Added

- Added `__all__` to every accessible module.

### Changed

- Changed the author name.
- The package will be published to PyPi through Trusted Publisher Management.

## [2.0.1] - 2025-06-03

### Added

- Added `src/game_state/utils.py` containing-
  - `_MissingSentinel` protected class.
  - `MISSING` variable (instance of `_MissingSentinel`).

### Changed

- Changed all examples to reflect v2.

### Fixed

- Fixed type errors in `State` and `StateManager` attributes.

## [2.0.0] - 2025-03-30

### Added

- Added state and global listeners: `on_setup`, `on_enter` & `on_leave`.
- Added state processors: `process_event` & `process_update`.
- Added `is_running` attribute to the `StateManager`.
- `StateManager.load_state` will raise `StateError` if the class passed is not subclassed from State.

### Changed

- No longer backward compatible with v1.x.x
- Changed the following methods to properties in the `StateManager`-
  - `get_current_state` method to `current_state` property.
  - `get_last_state` method to `last_state` property.
  - `get_state_map` method to `state_map` property.

### Removed

- Removed `__slots__` from the `StateManager` allowing users to add their own attributes to it.
- Removed the following methods of the StateManager-
  - `run_state`
  - `update_state`
- Removed the following methods from the State class-
  - `run`
  - `setup`
- Removed the following exceptions-
  - `ExitGame` error
  - `ExitState` error

## [1.1.3] - 2025-03-24

### Added

- Added examples on state hooks in `examples/state_hooks`.

### Changed

- Changed the raised error from `AssertionError` to `StateError` in the `StateManager.change_state` method upon passing an invalid state name.

### Fixed

- Fixed type errors in test cases.

## [1.1.2] - 2025-03-18

### Added

- Full support for python versions 3.8 - 3.13.
- Added state_name to the `__init_subclass__` of State.

### Removed

- Removed `State.clock` (The pygame clock).

## [1.1.1] - 2025-03-17

### Changed

- Changed `__states`, `__current_state` and `__last_state` to `_states`, `_current_state`, `_last_state` respectively, in the `StateManager`.
- Changed the docstyle from numpy to sphinx style.

### Fixed

- Fixed docstrings of classes & methods.
