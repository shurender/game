# Scratch Scripts & Tooling (`scratch/`)

This directory contains utility scripts, data generators, and development tools that are not part of the runtime game package.

---

## Script Inventory

| Script | Purpose |
| :--- | :--- |
| **`generate_content.py`** | Content synthesis script used to scaffold initial JSON databases (`creatures.json`, `moves.json`, `maps.json`, `quests.json`, `shops.json`, `trainers.json`). |

---

## Usage Notes

- Scripts in this directory are meant to be executed independently (e.g. `python scratch/generate_content.py`).
- Runtime code in `game/` must never depend on modules located inside `scratch/`.
