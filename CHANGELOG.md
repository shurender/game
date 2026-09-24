# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-09-24

### Added
- Complete playable region with 2 towns, 2 routes, 1 forest, 1 cave, and a major boss area.
- Over 20 fully implemented original creatures.
- Robust, data-driven game architecture parsing maps, NPCs, creatures, and items from JSON.
- Comprehensive save and load system with autosave.
- Built-in UI system with support for menus, settings, and quest logs.
- Procedural placeholder assets (images, sprites, sounds) ensuring zero crashes on missing files.
- Full battle engine with status effects, priority, speed, critical hits, and evolution.
- Quest and progression system.

### Optimized
- Eliminated redundant PyGame surface allocations, providing solid 60FPS on modern hardware.
- Streamlined rendering loop for state machine transitions.

### Fixed
- Fixed bug causing camera to occasionally drift from player view.
- Ensured 100% test passing rate across 215 automated tests.
