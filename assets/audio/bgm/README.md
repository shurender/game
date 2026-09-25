# Background Music (`assets/audio/bgm/`)

This directory contains looping background music tracks for game locations and events.

---

## File Naming Convention & Recommendations

| Track Name | Location / Event | Format |
| :--- | :--- | :--- |
| `town_peaceful.ogg` | Oakhaven (starting town) | Vorbis `.ogg`, 128-192 kbps |
| `route_1.ogg` | Route 1 wilderness | Vorbis `.ogg`, 128-192 kbps |
| `battle_wild.ogg` | Wild creature encounter | Vorbis `.ogg`, 128-192 kbps |
| `battle_trainer.ogg` | Trainer combat | Vorbis `.ogg`, 128-192 kbps |
| `victory.ogg` | Combat victory jingle | Vorbis `.ogg`, 128-192 kbps |

---

## Playback Behavior

- Streaming playback is executed through `pygame.mixer.music` to conserve RAM.
- Transitions between map areas employ a smooth 500 ms cross-fade managed by `MusicManager`.
