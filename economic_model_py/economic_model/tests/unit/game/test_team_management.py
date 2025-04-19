import unittest
from unittest.mock import patch, MagicMock
import uuid
import logging
import os
import pandas as pd
from china_growth_game.economic_model.game.team_management import (
    TeamManager,
    is_name_appropriate,
    ECONOMIC_ADJECTIVES,
    ECONOMIC_NOUNS,
    INAPPROPRIATE_WORDS,
    DEFAULT_SAVINGS_RATE,
    DEFAULT_EXCHANGE_RATE_POLICY,
    EXCHANGE_RATE_POLICIES
)
from china_growth_game.economic_model.utils.constants import (
    DEFAULT_PARAMS,
    E_1980,
    Y_STAR_1980,
    POLICY_MULTIPLIERS,
    DEFAULT_INITIAL_CONDITIONS
)

class TestTeamManagement(unittest.TestCase):
    """Test cases for the TeamManager class and related functions."""

    def setUp(self):
        """Set up the test environment."""
        self.team_manager = TeamManager()
        
    def test_is_name_appropriate(self):
        """Test the name appropriateness check function."""
        # Test appropriate names
        self.assertTrue(is_name_appropriate("Good Team"))
        self.assertTrue(is_name_appropriate("Team 123"))
        self.assertTrue(is_name_appropriate("Economic Tigers"))
        
        # Test inappropriate names
        for bad_word in INAPPROPRIATE_WORDS:
            self.assertFalse(is_name_appropriate(f"Team with {bad_word}"))
            self.assertFalse(is_name_appropriate(f"{bad_word.capitalize()} Team"))
            
        # Test case insensitivity
        self.assertFalse(is_name_appropriate(f"Team with {list(INAPPROPRIATE_WORDS)[0].upper()}"))
        
    def test_generate_team_name(self):
        """Test the team name generation function."""
        # Generate multiple names and check their structure
        for _ in range(10):
            name = self.team_manager.generate_team_name()
            self.assertIsInstance(name, str)
            self.assertTrue(name.startswith("The "))
            
            # Check that the name uses words from the predefined lists
            parts = name.split()
            self.assertEqual(len(parts), 3)  # "The", adjective, noun
            self.assertIn(parts[1], ECONOMIC_ADJECTIVES)
            self.assertIn(parts[2], ECONOMIC_NOUNS)
            
    def test_is_name_unique(self):
        """Test the name uniqueness check function."""
        # Create a team with a known name
        self.team_manager.create_team("Unique Team")
        
        # Check uniqueness
        self.assertTrue(self.team_manager.is_name_unique("Different Team"))
        self.assertFalse(self.team_manager.is_name_unique("Unique Team"))
        
        # Test case insensitivity
        self.assertFalse(self.team_manager.is_name_unique("UNIQUE TEAM"))
        self.assertFalse(self.team_manager.is_name_unique("unique team"))
        
    def test_create_team(self):
        """Test team creation."""
        # Create a team with a specified name
        team = self.team_manager.create_team("Test Team")
        self.assertIsInstance(team, dict)
        self.assertIn("team_id", team)
        self.assertEqual(team["team_name"], "Test Team")
        self.assertIn("current_state", team)
        self.assertIn("history", team)
        self.assertIn("decisions", team)
        self.assertFalse(team["eliminated"])
        
        # Check that initial state is set correctly
        self.assertEqual(team["current_state"]["year"], 1980)
        self.assertEqual(team["current_state"]["round"], 0)
        
        # Check that initial decision is set
        self.assertEqual(len(team["decisions"]), 1)
        self.assertEqual(team["decisions"][0]["round"], 0)
        self.assertEqual(team["decisions"][0]["year"], 1980)
        self.assertEqual(team["decisions"][0]["savings_rate"], DEFAULT_SAVINGS_RATE)
        self.assertEqual(team["decisions"][0]["exchange_rate_policy"], DEFAULT_EXCHANGE_RATE_POLICY)
        
        # Create a team with an auto-generated name
        auto_team = self.team_manager.create_team()
        self.assertIsInstance(auto_team["team_name"], str)
        self.assertGreater(len(auto_team["team_name"]), 0)
        
        # Test name uniqueness enforcement
        with self.assertRaises(ValueError):
            self.team_manager.create_team("Test Team")
            
        # Test inappropriate name rejection
        with self.assertRaises(ValueError):
            self.team_manager.create_team(f"Team with {list(INAPPROPRIATE_WORDS)[0]}")
            
        # Test maximum team limit
        for i in range(8):  # We already created 2 teams
            self.team_manager.create_team(f"Team {i+1}")
            
        # Creating an 11th team should fail
        with self.assertRaises(ValueError):
            self.team_manager.create_team("One Too Many")
            
    @patch('os.path.exists')
    @patch('pandas.read_csv')
    def test_init_with_csv(self, mock_read_csv, mock_exists):
        """Test initialization with CSV file."""
        # Mock CSV file existence and content
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.iloc.__getitem__().to_dict.return_value = {
            'Y': 400.0,
            'K': 900.0,
            'L': 700.0,
            'H': 1.2,
            'A': 1.1
        }
        mock_read_csv.return_value = mock_df
        
        # Create a new TeamManager that should use the mocked CSV
        csv_team_manager = TeamManager()
        
        # Check that the initial conditions were loaded from the CSV
        self.assertEqual(csv_team_manager.initial_conditions['Y'], 400.0)
        self.assertEqual(csv_team_manager.initial_conditions['K'], 900.0)
        
        # Test fallback to defaults when CSV read fails
        mock_read_csv.side_effect = Exception("CSV read error")
        fallback_team_manager = TeamManager()
        
        # The fallback should be to DEFAULT_INITIAL_CONDITIONS, not DEFAULT_PARAMS
        self.assertEqual(fallback_team_manager.initial_conditions, DEFAULT_INITIAL_CONDITIONS)
        
    def test_submit_decision(self):
        """Test decision submission."""
        # Create a team
        team = self.team_manager.create_team("Decision Team")
        team_id = team["team_id"]
        
        # Submit a valid decision
        decision = self.team_manager.submit_decision(
            team_id, 0.3, "market", 1, 1985
        )
        self.assertIsInstance(decision, dict)
        self.assertEqual(decision["round"], 1)
        self.assertEqual(decision["year"], 1985)
        self.assertEqual(decision["savings_rate"], 0.3)
        self.assertEqual(decision["exchange_rate_policy"], "market")
        self.assertIn("submitted_at", decision)
        
        # Check that the decision was added to the team
        self.assertEqual(len(self.team_manager.teams[team_id]["decisions"]), 2)  # Initial + new
        self.assertEqual(self.team_manager.teams[team_id]["decisions"][1], decision)
        
        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.team_manager.submit_decision("invalid-id", 0.3, "market", 1, 1985)
            
        # Test invalid savings rate
        with self.assertRaises(ValueError):
            self.team_manager.submit_decision(team_id, 1.5, "market", 1, 1985)
            
        with self.assertRaises(ValueError):
            self.team_manager.submit_decision(team_id, -0.1, "market", 1, 1985)
            
        # Test invalid exchange rate policy
        with self.assertRaises(ValueError):
            self.team_manager.submit_decision(team_id, 0.3, "invalid", 1, 1985)
            
        # Test submission for eliminated team
        self.team_manager.teams[team_id]["eliminated"] = True
        with self.assertRaises(ValueError):
            self.team_manager.submit_decision(team_id, 0.3, "market", 1, 1985)
            
    def test_get_team_state(self):
        """Test team state retrieval."""
        # Create a team
        team = self.team_manager.create_team("State Team")
        team_id = team["team_id"]
        
        # Get the team state
        state = self.team_manager.get_team_state(team_id)
        self.assertIsInstance(state, dict)
        self.assertEqual(state["team_id"], team_id)
        self.assertEqual(state["team_name"], "State Team")
        self.assertIn("current_state", state)
        self.assertIn("history", state)
        self.assertIn("decisions", state)
        
        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.team_manager.get_team_state("invalid-id")
            
    def test_get_team_data_for_game_state(self):
        """Test team data formatting for game state."""
        # Create a few teams
        team1 = self.team_manager.create_team("Team 1")
        team2 = self.team_manager.create_team("Team 2")
        
        # Get formatted team data
        team_data = self.team_manager.get_team_data_for_game_state()
        self.assertIsInstance(team_data, dict)
        self.assertEqual(len(team_data), 2)
        self.assertIn(team1["team_id"], team_data)
        self.assertIn(team2["team_id"], team_data)
        
        # Check that the data is formatted correctly
        for team_id, data in team_data.items():
            self.assertIn("team_id", data)
            self.assertIn("team_name", data)
            self.assertIn("current_state", data)
            self.assertIn("eliminated", data)
            self.assertNotIn("history", data)  # Should not include history
            self.assertNotIn("decisions", data)  # Should not include decisions
            
    def test_update_team_state(self):
        """Test team state update."""
        # Create a team
        team = self.team_manager.create_team("Update Team")
        team_id = team["team_id"]
        
        # Initial state
        initial_state = self.team_manager.teams[team_id]["current_state"].copy()
        
        # New state to update
        new_state = {
            "GDP": 1100.0,
            "Capital": 2200.0,
            "Labor Force": 110.0,
            "Human Capital": 1.1,
            "Productivity (TFP)": 1.6,
            "Net Exports": 50.0,
            "Consumption": 880.0,
            "Investment": 220.0
        }
        
        # Update the team state
        self.team_manager.update_team_state(team_id, new_state, 1985, 1)
        
        # Check that the state was updated
        updated_state = self.team_manager.teams[team_id]["current_state"]
        for key, value in new_state.items():
            self.assertEqual(updated_state[key], value)
            
        self.assertEqual(updated_state["year"], 1985)
        self.assertEqual(updated_state["round"], 1)
        
        # Check that the history was updated
        self.assertEqual(len(self.team_manager.teams[team_id]["history"]), 1)
        self.assertEqual(self.team_manager.teams[team_id]["history"][0], initial_state)
        
        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.team_manager.update_team_state("invalid-id", new_state, 1985, 1)
            
    def test_edit_team_name(self):
        """Test team name editing."""
        # Create a team
        team = self.team_manager.create_team("Original Name")
        team_id = team["team_id"]
        
        # Edit the team name
        updated_team = self.team_manager.edit_team_name(team_id, "New Name")
        self.assertEqual(updated_team["team_name"], "New Name")
        self.assertEqual(self.team_manager.teams[team_id]["team_name"], "New Name")
        
        # Create another team to test uniqueness
        self.team_manager.create_team("Another Team")
        
        # Test editing to a non-unique name
        with self.assertRaises(ValueError):
            self.team_manager.edit_team_name(team_id, "Another Team")
            
        # Test editing to an inappropriate name
        with self.assertRaises(ValueError):
            self.team_manager.edit_team_name(team_id, f"Team with {list(INAPPROPRIATE_WORDS)[0]}")
            
        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.team_manager.edit_team_name("invalid-id", "New Name")

if __name__ == '__main__':
    unittest.main()
