# Audio Assets (`assets/audio/`)

This directory is designated for external compressed audio streams, focusing on background music (BGM) and ambient soundscapes.

---

## Directory Layout

- **`bgm/`**: Background music files (recommended format: `.ogg` or `.mp3`, 44.1 kHz, stereo).
  - Loop points can be configured or tracks can loop indefinitely using `pygame.mixer.music.play(-1)`.

---

## Engine Integration

- Handled by `MusicManager` (`game/audio/music_manager.py`).
- Audio files placed here can be referenced in `maps.json` via the `"music"` field.
- If audio files are missing, the engine falls back to procedural tone generation without throwing errors.
