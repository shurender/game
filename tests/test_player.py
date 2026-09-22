"""Tests for the Player entity."""
from game.player.player import Player, Direction

def test_player_initial_position():
    player = Player(4, 6)
    assert player.x == 4
    assert player.y == 6
    assert player.facing == Direction.DOWN

def test_player_start_move():
    player = Player(4, 6)
    player.start_move(0, -1)
    
    assert player.x == 4
    assert player.y == 5
    assert player.facing == Direction.UP
    assert player.is_moving is True

def test_player_turn():
    player = Player(4, 6)
    player.turn(Direction.LEFT)
    
    assert player.facing == Direction.LEFT
    assert player.is_moving is False
    assert player.x == 4
    
def test_player_interaction_range():
    player = Player(4, 6)
    
    # Facing down
    player.turn(Direction.DOWN)
    ix, iy = player.interact()
    assert ix == 4 and iy == 7
    
    # Facing right
    player.turn(Direction.RIGHT)
    ix, iy = player.interact()
    assert ix == 5 and iy == 6
