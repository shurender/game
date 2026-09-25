# Map Environment Tiles (`assets/images/tiles/`)

This directory stores environmental terrain tilesets for the overworld and indoor locations.

---

## Specifications

- **Tile Unit**: 32×32 pixels per tile.
- **Tileset Layers**:
  - `tiles_ground.png`: Grass, dirt paths, water, wooden floorboards.
  - `tiles_decorations.png`: Fences, signs, bookshelves, counters, foliage.
  - `tiles_walls.png`: House exteriors, rooftops, cave walls, cliffs.
- **Engine Fallback**: In the absence of image tiles, `SpriteGenerator.get_tile_surface` builds procedural textures with grass blades, tree crowns, and brick patterns.
