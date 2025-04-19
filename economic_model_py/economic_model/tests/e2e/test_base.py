"""
Base class for end-to-end tests.

This module provides a base class for end-to-end tests that sets up the test environment
and provides utility methods for testing the complete game flow.
"""

import os
import unittest
import tempfile
import logging
from typing import Dict, List, Any, Optional

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.utils.persistence import PersistenceManager
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EndToEndTestBase(unittest.TestCase):
    """Base class for end-to-end tests."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for persistence
        self.temp_dir = tempfile.mkdtemp()

        # Create persistence manager
        self.persistence_manager = PersistenceManager(data_dir=self.temp_dir)

        # Create notification manager with test mode
        self.notification_manager = NotificationManager(test_mode=True)

        # Create game state with deterministic events
        self.game_state = GameState(
            persistence_manager=self.persistence_manager,
            notification_manager=self.notification_manager,
            use_randomized_events=True,  # Use randomized events for realistic testing
            random_seed=42,  # Use fixed seed for deterministic testing
            enable_replay=True  # Enable replay for debugging
        )

        # Track notifications for verification
        self.notifications = []
        self.notification_manager.add_listener(self._notification_listener)

    def tearDown(self):
        """Clean up the test environment."""
        # Clean up temporary directory
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)

        # Remove notification listener
        self.notification_manager.remove_listener(self._notification_listener)

    def _notification_listener(self, notification: Dict[str, Any]):
        """Listener for notifications."""
        self.notifications.append(notification)

    def create_test_teams(self, num_teams: int = 3) -> List[Dict[str, Any]]:
        """Create test teams for the game.

        Args:
            num_teams: Number of teams to create.

        Returns:
            List of created teams.
        """
        teams = []
        for i in range(num_teams):
            team_name = f"Test Team {i+1}"
            team = self.game_state.create_team(team_name)
            teams.append(team)
        return teams

    def start_game(self) -> Dict[str, Any]:
        """Start the game.

        Returns:
            Game state after starting.
        """
        return self.game_state.start_game()

    def submit_decisions(self, decisions: Dict[str, Dict[str, Any]]) -> None:
        """Submit decisions for teams.

        Args:
            decisions: Dictionary mapping team_id to decision parameters.
                Each decision should have 'savings_rate' and 'exchange_rate_policy'.
        """
        for team_id, decision in decisions.items():
            self.game_state.submit_decision(
                team_id=team_id,
                savings_rate=decision.get('savings_rate', 0.3),
                exchange_rate_policy=decision.get('exchange_rate_policy', 'market')
            )

    def process_round(self) -> Dict[str, Any]:
        """Process the current round.

        Returns:
            Result of processing the round.
        """
        return self.game_state.advance_round()

    def run_full_game(self, num_teams: int = 3, decisions_strategy: str = 'default') -> Dict[str, Any]:
        """Run a full game from start to finish.

        Args:
            num_teams: Number of teams to create.
            decisions_strategy: Strategy for team decisions.
                'default': Use default values.
                'random': Use random values.
                'optimal': Use optimal values based on economic theory.

        Returns:
            Final game state.
        """
        # Create teams
        teams = self.create_test_teams(num_teams)
        team_ids = [team['team_id'] for team in teams]

        # Start game
        self.start_game()

        # Run through all rounds
        for round_num in range(len(self.game_state.years) - 1):  # -1 because we start at round 0
            # Generate decisions based on strategy
            decisions = {}
            for team_id in team_ids:
                if decisions_strategy == 'default':
                    decisions[team_id] = {
                        'savings_rate': 0.3,
                        'exchange_rate_policy': 'market'
                    }
                elif decisions_strategy == 'random':
                    import random
                    decisions[team_id] = {
                        'savings_rate': random.uniform(0.1, 0.5),
                        'exchange_rate_policy': random.choice(['market', 'undervalue', 'overvalue'])
                    }
                elif decisions_strategy == 'optimal':
                    # In a real implementation, this would use economic theory to determine optimal decisions
                    decisions[team_id] = {
                        'savings_rate': 0.4,  # Higher savings rate for faster capital accumulation
                        'exchange_rate_policy': 'undervalue'  # Undervalue for export-led growth
                    }

            # Submit decisions
            self.submit_decisions(decisions)

            # Process round
            self.process_round()

        # Return final game state
        return self.game_state.get_game_state()

    def verify_game_state(self, game_state: Dict[str, Any]) -> None:
        """Verify that the game state is valid.

        Args:
            game_state: Game state to verify.
        """
        # Verify basic game state properties
        self.assertIsNotNone(game_state.get('game_id'))
        self.assertIsNotNone(game_state.get('current_round'))
        self.assertIsNotNone(game_state.get('current_year'))
        self.assertTrue(game_state.get('game_started'))

        # Verify teams
        teams = game_state.get('teams', {})
        self.assertGreater(len(teams), 0)

        # Verify each team
        for team_id, team in teams.items():
            self.assertIsNotNone(team.get('team_id'))
            self.assertIsNotNone(team.get('team_name'))
            self.assertIsNotNone(team.get('current_state'))
            # Check for either history or current_state
            self.assertTrue(team.get('history') is not None or team.get('current_state') is not None)

            # Verify team history if it exists
            if team.get('history') is not None:
                history = team.get('history', [])
                self.assertGreater(len(history), 0)

            # Verify current state
            current_state = team.get('current_state', {})
            # Handle different state structure formats for GDP
            self.assertTrue(
                current_state.get('gdp') is not None or
                current_state.get('GDP') is not None
            )
            # Handle different state structure formats for capital
            self.assertTrue(
                current_state.get('capital') is not None or
                current_state.get('Capital') is not None
            )
            # Handle different state structure formats for labor
            self.assertTrue(
                current_state.get('labor') is not None or
                current_state.get('Labor Force') is not None
            )
            # Handle different state structure formats for productivity
            self.assertTrue(
                current_state.get('tfp') is not None or
                current_state.get('Productivity (TFP)') is not None
            )

    def verify_notifications(self, expected_types: List[str]) -> None:
        """Verify that the expected notification types were sent.

        Args:
            expected_types: List of expected notification types.
        """
        notification_types = [n.get('type') for n in self.notifications]
        for expected_type in expected_types:
            self.assertIn(expected_type, notification_types)

    def verify_prizes(self, game_state: Dict[str, Any], expected_prizes: Dict[str, List[str]]) -> None:
        """Verify that the expected prizes were awarded.

        Args:
            game_state: Game state to verify.
            expected_prizes: Dictionary mapping team_id to list of expected prize types.
        """
        # Get awarded prizes
        awarded_prizes = {}
        for team_id, team in game_state.get('teams', {}).items():
            awarded_prizes[team_id] = [p.get('type') for p in team.get('prizes', [])]

        # Verify prizes
        for team_id, expected in expected_prizes.items():
            actual = awarded_prizes.get(team_id, [])
            for prize_type in expected:
                self.assertIn(prize_type, actual)

    def verify_events(self, expected_events: List[str]) -> None:
        """Verify that the expected events occurred.

        Args:
            expected_events: List of expected event types.
        """
        # Get events from notifications
        event_notifications = [n for n in self.notifications if n.get('type') == 'event']
        event_types = [n.get('event', {}).get('type') for n in event_notifications]

        # Verify events
        for expected_event in expected_events:
            self.assertIn(expected_event, event_types)
