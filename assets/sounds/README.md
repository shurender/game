# Sound Effects Directory (`assets/sounds/`)

This directory contains standalone digital sound effects (SFX) that complement the engine's built-in procedural synthesizer.

---

## Subdirectories

- **`sfx/`**: Short audio clips (.wav or .ogg) for UI beeps, combat hits, creature cries, and door opens.

---

## Audio Pipeline

The engine prioritizes high-fidelity digital audio if present in `sfx/`, and seamlessly falls back to `AudioManager.synthesize_tone()` if no files are found.
