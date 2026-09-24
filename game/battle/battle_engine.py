import random
from typing import List

from game.battle.battle import Battle
from game.battle.battle_action import BattleAction
from game.battle.battle_result import ActionEvent, TurnResult
from game.battle.damage import calculate_damage, calculate_accuracy
from game.battle.status_effects import StatusEffect


def _award_battle_xp(winner, defeated):
    """Award XP to the winner based on the defeated creature's species data."""
    from game.creatures.creature_factory import CreatureFactory
    from game.creatures.progression import award_xp, calculate_battle_xp

    cf = CreatureFactory.get_instance()
    defeated_raw = cf.get_raw(defeated.species.species_id) or {}
    winner_raw = cf.get_raw(winner.species.species_id) or {}

    xp = calculate_battle_xp(defeated_raw, winner.level)
    return award_xp(winner, xp, winner_raw)



class BattleEngine:
    """Processes turn actions and updates battle state."""
    
    @staticmethod
    def process_turn(battle: Battle, action1: BattleAction, action2: BattleAction) -> TurnResult:
        result = TurnResult()
        
        # Determine order
        actions = [action1, action2]
        actions.sort(key=lambda a: (a.priority, a.speed, random.random()), reverse=True)
        
        for action in actions:
            if battle.is_over:
                break
                
            if action.actor.is_fainted:
                continue
                
            event = BattleEngine._process_action(battle, action)
            result.events.append(event)
            
            # Check win conditions
            if battle.enemy_creature.is_fainted:
                battle.is_over = True
                battle.winner = "PLAYER"
                result.events.append(ActionEvent(
                    actor_name=battle.enemy_creature.name,
                    action_type="FAINT",
                    message=f"{battle.enemy_creature.name} fainted!",
                    fainted=True
                ))
                # Award XP to the player's creature
                result.xp_result = _award_battle_xp(
                    battle.player_creature, battle.enemy_creature
                )
                if result.xp_result.xp_gained > 0:
                    result.events.append(ActionEvent(
                        actor_name=battle.player_creature.name,
                        action_type="XP_GAIN",
                        message=f"{battle.player_creature.name} gained {result.xp_result.xp_gained} XP!"
                    ))
                for lvl_result in result.xp_result.level_ups:
                    result.events.append(ActionEvent(
                        actor_name=battle.player_creature.name,
                        action_type="LEVEL_UP",
                        message=f"{battle.player_creature.name} grew to level {lvl_result.new_level}!"
                    ))
                    for move_id in lvl_result.moves_learned:
                        result.events.append(ActionEvent(
                            actor_name=battle.player_creature.name,
                            action_type="MOVE_LEARNED",
                            message=f"{battle.player_creature.name} learned a new move!"
                        ))
                if result.xp_result.pending_evolution:
                    result.events.append(ActionEvent(
                        actor_name=battle.player_creature.name,
                        action_type="EVOLUTION_READY",
                        message=f"{battle.player_creature.name} is ready to evolve!"
                    ))
                break
            elif battle.player_creature.is_fainted:
                battle.is_over = True
                battle.winner = "ENEMY"
                result.events.append(ActionEvent(
                    actor_name=battle.player_creature.name,
                    action_type="FAINT",
                    message=f"{battle.player_creature.name} fainted!",
                    fainted=True
                ))
                break
            elif battle.is_over: # e.g., escaped
                break
                
        result.battle_ended = battle.is_over

        result.winner = battle.winner
        return result

    @staticmethod
    def _process_action(battle: Battle, action: BattleAction) -> ActionEvent:
        if action.action_type == "ESCAPE":
            # Simple escape logic
            # In a real game, this might fail based on speeds.
            success = True
            if action.actor == battle.player_creature:
                if success:
                    battle.is_over = True
                    battle.winner = "ESCAPE"
                    return ActionEvent(
                        actor_name=action.actor.name,
                        action_type="ESCAPE",
                        message=f"{action.actor.name} escaped!",
                        escaped=True
                    )
            return ActionEvent(
                actor_name=action.actor.name,
                action_type="ESCAPE_FAIL",
                message=f"{action.actor.name} failed to escape!"
            )
            
        elif action.action_type == "SWITCH":
            # Swap active creature
            new_creature = action.target
            old_name = action.actor.name
            if action.actor == battle.player_creature:
                battle.player_creature = new_creature
            else:
                battle.enemy_creature = new_creature
                
            return ActionEvent(
                actor_name=old_name,
                action_type="SWITCH",
                message=f"{old_name} was swapped for {new_creature.name}!"
            )
            
        elif action.action_type == "MOVE":
            return BattleEngine._process_move(action)
            
        return ActionEvent(
            actor_name=action.actor.name,
            action_type="UNKNOWN",
            message=f"{action.actor.name} did nothing."
        )
        
    @staticmethod
    def _process_move(action: BattleAction) -> ActionEvent:
        move = action.move
        actor = action.actor
        target = action.target
        
        event = ActionEvent(
            actor_name=actor.name,
            action_type="MOVE",
            message=f"{actor.name} used {move.name}!"
        )
        
        if not calculate_accuracy(move):
            event.message += f"\n{actor.name}'s attack missed!"
            event.missed = True
            return event

            
        damage, effectiveness, is_critical = calculate_damage(actor, target, move)
        
        event.damage_dealt = damage
        event.is_critical = is_critical
        event.effectiveness = effectiveness
        
        if effectiveness == 0:
            event.message += "\nIt had no effect..."
            return event
            
        target.take_damage(damage)
        
        if is_critical:
            event.message += "\nA critical hit!"
            
        if effectiveness > 1.0:
            event.message += "\nIt's super effective!"
        elif effectiveness < 1.0:
            event.message += "\nIt's not very effective..."
            
        if move.status_effect and target.current_hp > 0:
            try:
                status_enum = getattr(StatusEffect, move.status_effect.upper())
                # Use name to check if none to be robust, some might have it as enum, some as str
                is_none = False
                if hasattr(target, 'status'):
                    if isinstance(target.status, str) and target.status == "NONE":
                        is_none = True
                    elif hasattr(target.status, 'name') and target.status.name == "NONE":
                        is_none = True
                if is_none or not hasattr(target, 'status'):
                    target.status = status_enum
                    event.status_applied = status_enum.name
                    event.message += f"\n{target.name} was afflicted with {status_enum.name}!"
            except AttributeError:
                pass
                
        return event
