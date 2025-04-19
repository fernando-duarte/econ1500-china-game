"""
Replay Manager for the China Growth Game.

This module provides functionality for recording and replaying game states
for debugging, auditing, and demonstration purposes.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from copy import deepcopy

from economic_model_py.economic_model.utils.json_utils import convert_numpy_values, numpy_safe_json_dumps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplayManager:
    """
    Manages recording and replaying of game states.
    
    This class provides functionality to:
    1. Record game states at each step
    2. Save recorded states to disk
    3. Load recorded states from disk
    4. Replay game states step by step
    """
    
    def __init__(self, replay_dir: str = None):
        """
        Initialize the replay manager.
        
        Args:
            replay_dir: Directory to store replay files. If None, uses a default directory.
        """
        if replay_dir is None:
            # Use a default directory in the current directory
            self.replay_dir = os.path.join(os.getcwd(), 'replays')
        else:
            self.replay_dir = replay_dir
            
        # Create the replay directory if it doesn't exist
        os.makedirs(self.replay_dir, exist_ok=True)
        
        # Initialize replay data
        self.reset()
        
    def reset(self):
        """Reset the replay manager to its initial state."""
        self.replay_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.game_id = None
        self.states = []
        self.decisions = {}  # Map of round -> team_id -> decision
        self.events = {}  # Map of round -> events
        self.current_replay_index = -1
        self.is_recording = False
        self.is_replaying = False
        
    def start_recording(self, game_id: str):
        """
        Start recording a new game session.
        
        Args:
            game_id: The ID of the game to record.
        """
        self.reset()
        self.game_id = game_id
        self.is_recording = True
        logger.info(f"Started recording game {game_id} with replay ID {self.replay_id}")
        
    def stop_recording(self) -> str:
        """
        Stop recording and save the replay.
        
        Returns:
            The ID of the saved replay.
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return None
            
        self.is_recording = False
        self._save_replay()
        logger.info(f"Stopped recording game {self.game_id}, saved replay {self.replay_id}")
        return self.replay_id
        
    def record_state(self, state: Dict[str, Any]):
        """
        Record a game state.
        
        Args:
            state: The game state to record.
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return
            
        # Make a deep copy to avoid modifying the original state
        state_copy = deepcopy(state)
        
        # Convert numpy values to Python native types
        state_copy = convert_numpy_values(state_copy)
        
        # Add timestamp
        state_copy['recorded_at'] = datetime.now().isoformat()
        
        # Add to states list
        self.states.append(state_copy)
        logger.debug(f"Recorded state for round {state_copy.get('current_round', 'unknown')}")
        
    def record_decision(self, team_id: str, round_num: int, decision: Dict[str, Any]):
        """
        Record a team's decision.
        
        Args:
            team_id: The ID of the team making the decision.
            round_num: The round number for the decision.
            decision: The decision data.
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return
            
        # Initialize round if not exists
        if round_num not in self.decisions:
            self.decisions[round_num] = {}
            
        # Make a deep copy to avoid modifying the original decision
        decision_copy = deepcopy(decision)
        
        # Convert numpy values to Python native types
        decision_copy = convert_numpy_values(decision_copy)
        
        # Add timestamp
        decision_copy['recorded_at'] = datetime.now().isoformat()
        
        # Add to decisions map
        self.decisions[round_num][team_id] = decision_copy
        logger.debug(f"Recorded decision for team {team_id} in round {round_num}")
        
    def record_events(self, round_num: int, events: List[Dict[str, Any]]):
        """
        Record events for a round.
        
        Args:
            round_num: The round number.
            events: List of events for the round.
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return
            
        # Make a deep copy to avoid modifying the original events
        events_copy = deepcopy(events)
        
        # Convert numpy values to Python native types
        events_copy = convert_numpy_values(events_copy)
        
        # Add to events map
        self.events[round_num] = events_copy
        logger.debug(f"Recorded {len(events_copy)} events for round {round_num}")
        
    def _save_replay(self) -> bool:
        """
        Save the current replay to disk.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create replay data
            replay_data = {
                'replay_id': self.replay_id,
                'created_at': self.created_at,
                'game_id': self.game_id,
                'states': self.states,
                'decisions': self.decisions,
                'events': self.events
            }
            
            # Create filename
            filename = f"{self.replay_id}.json"
            filepath = os.path.join(self.replay_dir, filename)
            
            # Save to file
            with open(filepath, 'w') as f:
                f.write(numpy_safe_json_dumps(replay_data))
                
            logger.info(f"Saved replay to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving replay: {str(e)}")
            return False
            
    def load_replay(self, replay_id: str) -> bool:
        """
        Load a replay from disk.
        
        Args:
            replay_id: The ID of the replay to load.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create filename
            filename = f"{replay_id}.json"
            filepath = os.path.join(self.replay_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                logger.error(f"Replay file {filepath} not found")
                return False
                
            # Load from file
            with open(filepath, 'r') as f:
                replay_data = json.loads(f.read())
                
            # Set replay data
            self.replay_id = replay_data.get('replay_id', str(uuid.uuid4()))
            self.created_at = replay_data.get('created_at', datetime.now().isoformat())
            self.game_id = replay_data.get('game_id')
            self.states = replay_data.get('states', [])
            self.decisions = replay_data.get('decisions', {})
            self.events = replay_data.get('events', {})
            self.current_replay_index = -1
            self.is_recording = False
            self.is_replaying = True
            
            logger.info(f"Loaded replay {replay_id} with {len(self.states)} states")
            return True
        except Exception as e:
            logger.error(f"Error loading replay: {str(e)}")
            return False
            
    def start_replay(self) -> Optional[Dict[str, Any]]:
        """
        Start replaying from the beginning.
        
        Returns:
            The initial game state, or None if no replay is loaded.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return None
            
        if not self.states:
            logger.warning("Replay has no states")
            return None
            
        self.current_replay_index = 0
        logger.info(f"Started replaying from state 0")
        return self.states[0]
        
    def next_state(self) -> Optional[Dict[str, Any]]:
        """
        Advance to the next state in the replay.
        
        Returns:
            The next game state, or None if at the end of the replay.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return None
            
        if not self.states:
            logger.warning("Replay has no states")
            return None
            
        if self.current_replay_index >= len(self.states) - 1:
            logger.info("Reached end of replay")
            return None
            
        self.current_replay_index += 1
        logger.info(f"Advanced to state {self.current_replay_index}")
        return self.states[self.current_replay_index]
        
    def previous_state(self) -> Optional[Dict[str, Any]]:
        """
        Go back to the previous state in the replay.
        
        Returns:
            The previous game state, or None if at the beginning of the replay.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return None
            
        if not self.states:
            logger.warning("Replay has no states")
            return None
            
        if self.current_replay_index <= 0:
            logger.info("Already at beginning of replay")
            return None
            
        self.current_replay_index -= 1
        logger.info(f"Went back to state {self.current_replay_index}")
        return self.states[self.current_replay_index]
        
    def jump_to_round(self, round_num: int) -> Optional[Dict[str, Any]]:
        """
        Jump to a specific round in the replay.
        
        Args:
            round_num: The round number to jump to.
            
        Returns:
            The game state for the specified round, or None if not found.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return None
            
        if not self.states:
            logger.warning("Replay has no states")
            return None
            
        # Find the state with the matching round number
        for i, state in enumerate(self.states):
            if state.get('current_round') == round_num:
                self.current_replay_index = i
                logger.info(f"Jumped to round {round_num} (state {i})")
                return state
                
        logger.warning(f"Round {round_num} not found in replay")
        return None
        
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the current state in the replay.
        
        Returns:
            The current game state, or None if no replay is loaded.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return None
            
        if not self.states:
            logger.warning("Replay has no states")
            return None
            
        if self.current_replay_index < 0 or self.current_replay_index >= len(self.states):
            logger.warning("Invalid replay index")
            return None
            
        return self.states[self.current_replay_index]
        
    def get_decisions_for_round(self, round_num: int) -> Dict[str, Dict[str, Any]]:
        """
        Get all decisions for a specific round.
        
        Args:
            round_num: The round number.
            
        Returns:
            Dictionary mapping team_id to decision data.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return {}
            
        return self.decisions.get(str(round_num), {})
        
    def get_events_for_round(self, round_num: int) -> List[Dict[str, Any]]:
        """
        Get all events for a specific round.
        
        Args:
            round_num: The round number.
            
        Returns:
            List of events for the round.
        """
        if not self.is_replaying:
            logger.warning("No replay loaded")
            return []
            
        return self.events.get(str(round_num), [])
        
    def get_replay_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current replay.
        
        Returns:
            Dictionary with replay metadata.
        """
        return {
            'replay_id': self.replay_id,
            'created_at': self.created_at,
            'game_id': self.game_id,
            'state_count': len(self.states),
            'round_count': len(set(state.get('current_round', -1) for state in self.states)),
            'current_index': self.current_replay_index,
            'is_recording': self.is_recording,
            'is_replaying': self.is_replaying
        }
        
    def list_available_replays(self) -> List[Dict[str, Any]]:
        """
        List all available replay files.
        
        Returns:
            List of dictionaries with replay metadata.
        """
        replays = []
        
        try:
            # Get all JSON files in the replay directory
            for filename in os.listdir(self.replay_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.replay_dir, filename)
                    
                    try:
                        # Load basic metadata
                        with open(filepath, 'r') as f:
                            data = json.loads(f.read())
                            
                        replays.append({
                            'replay_id': data.get('replay_id'),
                            'created_at': data.get('created_at'),
                            'game_id': data.get('game_id'),
                            'state_count': len(data.get('states', [])),
                            'filename': filename
                        })
                    except Exception as e:
                        logger.error(f"Error loading replay metadata from {filepath}: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing replays: {str(e)}")
            
        return replays
        
    def delete_replay(self, replay_id: str) -> bool:
        """
        Delete a replay file.
        
        Args:
            replay_id: The ID of the replay to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create filename
            filename = f"{replay_id}.json"
            filepath = os.path.join(self.replay_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                logger.error(f"Replay file {filepath} not found")
                return False
                
            # Delete file
            os.remove(filepath)
            logger.info(f"Deleted replay {replay_id}")
            
            # Reset if this was the current replay
            if self.replay_id == replay_id:
                self.reset()
                
            return True
        except Exception as e:
            logger.error(f"Error deleting replay: {str(e)}")
            return False
