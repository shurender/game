# Audio Subsystem (`game/audio/`)

The `audio` package manages sound effects (SFX) and background music (BGM). It features procedural tone synthesis using `numpy` so that the game can produce authentic retro 8-bit sound effects without requiring external `.wav` or `.ogg` audio files.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`audio_manager.py`** | `AudioManager`. Central audio coordinator. Generates synthesized audio waveforms (sine, square, triangle), manages SFX playback and caching, and regulates master volume. |
| **`music_manager.py`** | `MusicManager`. Handles streaming background music tracks, smooth fade-ins/fade-outs, volume scaling, and map-to-music route associations. |

---

## Procedural Waveform Synthesis

`AudioManager.synthesize_tone(name, frequency, duration, wave, volume)` uses `numpy` arrays to build sound buffers directly in memory:
- **Sine**: Smooth melodic chimes (menu confirms, level-up fanfares).
- **Square**: Classic 8-bit chiptune bleeps (hit impacts, cursor movements).
- **Triangle**: Soft, hollow tones (capture ball wobbles, gentle bumps).
- **Envelopes**: Linear attack and release envelopes are applied to eliminate audio pops and clicks.
- **Headless Safety**: If the system has no active audio output (e.g. CI environments), tone generation and playback safely fall back to no-ops without throwing exceptions.

---

## Volume Controls

```
Master Volume (0.0 - 1.0)
     ├── SFX Volume (scaled by Master)
     └── BGM Volume (scaled by Master)
```

Settings are dynamically synced with `SettingsManager` and saved to `saves/settings.json`.
