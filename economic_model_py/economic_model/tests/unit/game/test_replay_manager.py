"""
Unit tests for the ReplayManager class.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from economic_model_py.economic_model.game.replay_manager import ReplayManager

class TestReplayManager(unittest.TestCase):
    """Test cases for the ReplayManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for replay files
        self.temp_dir = tempfile.mkdtemp()
        self.replay_manager = ReplayManager(replay_dir=self.temp_dir)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
        
    def test_init(self):
        """Test initialization of ReplayManager."""
        self.assertIsNotNone(self.replay_manager.replay_id)
        self.assertIsNotNone(self.replay_manager.created_at)
        self.assertIsNone(self.replay_manager.game_id)
        self.assertEqual(self.replay_manager.states, [])
        self.assertEqual(self.replay_manager.decisions, {})
        self.assertEqual(self.replay_manager.events, {})
        self.assertEqual(self.replay_manager.current_replay_index, -1)
        self.assertFalse(self.replay_manager.is_recording)
        self.assertFalse(self.replay_manager.is_replaying)
        
    def test_start_recording(self):
        """Test starting recording."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        self.assertEqual(self.replay_manager.game_id, game_id)
        self.assertTrue(self.replay_manager.is_recording)
        
    def test_record_state(self):
        """Test recording a state."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        state = {
            "current_round": 0,
            "current_year": 1980,
            "teams": {
                "team1": {"team_name": "Team 1"}
            }
        }
        
        self.replay_manager.record_state(state)
        
        self.assertEqual(len(self.replay_manager.states), 1)
        self.assertEqual(self.replay_manager.states[0]["current_round"], 0)
        self.assertEqual(self.replay_manager.states[0]["current_year"], 1980)
        self.assertIn("team1", self.replay_manager.states[0]["teams"])
        self.assertIn("recorded_at", self.replay_manager.states[0])
        
    def test_record_decision(self):
        """Test recording a decision."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        team_id = "team1"
        round_num = 0
        decision = {
            "savings_rate": 0.2,
            "exchange_rate_policy": "market"
        }
        
        self.replay_manager.record_decision(team_id, round_num, decision)
        
        self.assertIn(round_num, self.replay_manager.decisions)
        self.assertIn(team_id, self.replay_manager.decisions[round_num])
        self.assertEqual(self.replay_manager.decisions[round_num][team_id]["savings_rate"], 0.2)
        self.assertEqual(self.replay_manager.decisions[round_num][team_id]["exchange_rate_policy"], "market")
        self.assertIn("recorded_at", self.replay_manager.decisions[round_num][team_id])
        
    def test_record_events(self):
        """Test recording events."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        round_num = 0
        events = [
            {
                "name": "WTO Accession",
                "year": 2001,
                "effects": {"tfp_increase": 0.05}
            }
        ]
        
        self.replay_manager.record_events(round_num, events)
        
        self.assertIn(round_num, self.replay_manager.events)
        self.assertEqual(len(self.replay_manager.events[round_num]), 1)
        self.assertEqual(self.replay_manager.events[round_num][0]["name"], "WTO Accession")
        self.assertEqual(self.replay_manager.events[round_num][0]["year"], 2001)
        self.assertEqual(self.replay_manager.events[round_num][0]["effects"]["tfp_increase"], 0.05)
        
    def test_save_and_load_replay(self):
        """Test saving and loading a replay."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        # Record some data
        state = {"current_round": 0, "current_year": 1980}
        self.replay_manager.record_state(state)
        
        team_id = "team1"
        round_num = 0
        decision = {"savings_rate": 0.2, "exchange_rate_policy": "market"}
        self.replay_manager.record_decision(team_id, round_num, decision)
        
        events = [{"name": "WTO Accession", "year": 2001}]
        self.replay_manager.record_events(round_num, events)
        
        # Stop recording and save
        replay_id = self.replay_manager.stop_recording()
        
        # Create a new replay manager and load the replay
        new_replay_manager = ReplayManager(replay_dir=self.temp_dir)
        success = new_replay_manager.load_replay(replay_id)
        
        self.assertTrue(success)
        self.assertEqual(new_replay_manager.game_id, game_id)
        self.assertEqual(len(new_replay_manager.states), 1)
        self.assertEqual(new_replay_manager.states[0]["current_round"], 0)
        self.assertIn(round_num, new_replay_manager.decisions)
        self.assertIn(team_id, new_replay_manager.decisions[round_num])
        self.assertIn(round_num, new_replay_manager.events)
        
    def test_replay_navigation(self):
        """Test replay navigation (next, previous, jump)."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        # Record multiple states
        for i in range(5):
            state = {"current_round": i, "current_year": 1980 + i * 5}
            self.replay_manager.record_state(state)
            
        # Stop recording and save
        replay_id = self.replay_manager.stop_recording()
        
        # Load the replay
        self.replay_manager.load_replay(replay_id)
        
        # Start replay
        initial_state = self.replay_manager.start_replay()
        self.assertEqual(initial_state["current_round"], 0)
        self.assertEqual(self.replay_manager.current_replay_index, 0)
        
        # Next state
        next_state = self.replay_manager.next_state()
        self.assertEqual(next_state["current_round"], 1)
        self.assertEqual(self.replay_manager.current_replay_index, 1)
        
        # Next state again
        next_state = self.replay_manager.next_state()
        self.assertEqual(next_state["current_round"], 2)
        self.assertEqual(self.replay_manager.current_replay_index, 2)
        
        # Previous state
        prev_state = self.replay_manager.previous_state()
        self.assertEqual(prev_state["current_round"], 1)
        self.assertEqual(self.replay_manager.current_replay_index, 1)
        
        # Jump to round 3
        jump_state = self.replay_manager.jump_to_round(3)
        self.assertEqual(jump_state["current_round"], 3)
        self.assertEqual(self.replay_manager.current_replay_index, 3)
        
        # Jump to non-existent round
        jump_state = self.replay_manager.jump_to_round(10)
        self.assertIsNone(jump_state)
        
    def test_list_available_replays(self):
        """Test listing available replays."""
        # Create a few replays
        for i in range(3):
            game_id = f"test_game_{i}"
            self.replay_manager.start_recording(game_id)
            state = {"current_round": 0, "current_year": 1980}
            self.replay_manager.record_state(state)
            self.replay_manager.stop_recording()
            
        # List replays
        replays = self.replay_manager.list_available_replays()
        
        self.assertEqual(len(replays), 3)
        for replay in replays:
            self.assertIn("replay_id", replay)
            self.assertIn("created_at", replay)
            self.assertIn("game_id", replay)
            self.assertIn("state_count", replay)
            
    def test_delete_replay(self):
        """Test deleting a replay."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        state = {"current_round": 0, "current_year": 1980}
        self.replay_manager.record_state(state)
        
        replay_id = self.replay_manager.stop_recording()
        
        # Verify replay exists
        replays_before = self.replay_manager.list_available_replays()
        self.assertEqual(len(replays_before), 1)
        
        # Delete replay
        success = self.replay_manager.delete_replay(replay_id)
        self.assertTrue(success)
        
        # Verify replay is deleted
        replays_after = self.replay_manager.list_available_replays()
        self.assertEqual(len(replays_after), 0)
        
    def test_get_replay_metadata(self):
        """Test getting replay metadata."""
        game_id = "test_game_id"
        self.replay_manager.start_recording(game_id)
        
        for i in range(3):
            state = {"current_round": i, "current_year": 1980 + i * 5}
            self.replay_manager.record_state(state)
            
        replay_id = self.replay_manager.stop_recording()
        
        # Load the replay
        self.replay_manager.load_replay(replay_id)
        
        # Get metadata
        metadata = self.replay_manager.get_replay_metadata()
        
        self.assertEqual(metadata["replay_id"], replay_id)
        self.assertEqual(metadata["game_id"], game_id)
        self.assertEqual(metadata["state_count"], 3)
        self.assertEqual(metadata["round_count"], 3)
        self.assertEqual(metadata["current_index"], -1)
        self.assertFalse(metadata["is_recording"])
        self.assertTrue(metadata["is_replaying"])
        
if __name__ == "__main__":
    unittest.main()
