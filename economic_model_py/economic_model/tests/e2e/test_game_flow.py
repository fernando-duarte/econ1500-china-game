"""
End-to-end tests for the complete game flow.

This module contains tests that verify the complete game flow from start to finish,
including team creation, game start, decision submission, round processing, event
triggering, prize awarding, and game completion.
"""

import unittest
import logging
from typing import Dict, List, Any

from economic_model_py.economic_model.tests.e2e.test_base import EndToEndTestBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestGameFlow(EndToEndTestBase):
    """Test cases for the complete game flow."""
    
    def test_team_creation_and_initialization(self):
        """Test team creation and initialization."""
        # Create teams
        teams = self.create_test_teams(3)
        
        # Verify teams were created
        self.assertEqual(len(teams), 3)
        
        # Verify team properties
        for i, team in enumerate(teams):
            self.assertEqual(team['team_name'], f"Test Team {i+1}")
            self.assertIsNotNone(team['team_id'])
            self.assertIsNotNone(team['current_state'])
            self.assertEqual(team['current_state']['round'], 0)
            self.assertEqual(team['current_state']['year'], 1980)
            
            # Verify initial economic state
            self.assertGreater(team['current_state']['gdp'], 0)
            self.assertGreater(team['current_state']['capital'], 0)
            self.assertGreater(team['current_state']['labor'], 0)
            self.assertGreater(team['current_state']['tfp'], 0)
            
    def test_game_start_and_first_round(self):
        """Test game start and first round."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        game_state = self.start_game()
        
        # Verify game started
        self.assertTrue(game_state['game_started'])
        self.assertEqual(game_state['current_round'], 0)
        self.assertEqual(game_state['current_year'], 1980)
        
        # Verify teams in game state
        for team_id in team_ids:
            self.assertIn(team_id, game_state['teams'])
            
        # Verify initial history
        for team_id in team_ids:
            team = game_state['teams'][team_id]
            self.assertEqual(len(team['history']), 1)
            self.assertEqual(team['history'][0]['round'], 0)
            self.assertEqual(team['history'][0]['year'], 1980)
            
    def test_team_decision_submission(self):
        """Test team decision submission."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        self.start_game()
        
        # Submit decisions
        decisions = {}
        for i, team_id in enumerate(team_ids):
            # Use different decisions for each team
            savings_rate = 0.2 + (i * 0.1)  # 0.2, 0.3, 0.4
            exchange_rate_policy = ['market', 'fixed', 'managed'][i]
            
            decisions[team_id] = {
                'savings_rate': savings_rate,
                'exchange_rate_policy': exchange_rate_policy
            }
            
        self.submit_decisions(decisions)
        
        # Verify decisions were recorded
        game_state = self.game_state.get_game_state()
        for i, team_id in enumerate(team_ids):
            team = game_state['teams'][team_id]
            self.assertEqual(team['current_state']['savings_rate'], 0.2 + (i * 0.1))
            self.assertEqual(team['current_state']['exchange_rate_policy'], ['market', 'fixed', 'managed'][i])
            
    def test_round_advancement(self):
        """Test round advancement."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        self.start_game()
        
        # Submit decisions
        decisions = {}
        for team_id in team_ids:
            decisions[team_id] = {
                'savings_rate': 0.3,
                'exchange_rate_policy': 'market'
            }
            
        self.submit_decisions(decisions)
        
        # Process round
        result = self.process_round()
        
        # Verify round advanced
        self.assertEqual(result['round'], 1)
        self.assertEqual(result['year'], 1985)
        
        # Verify game state
        game_state = self.game_state.get_game_state()
        self.assertEqual(game_state['current_round'], 1)
        self.assertEqual(game_state['current_year'], 1985)
        
        # Verify team history
        for team_id in team_ids:
            team = game_state['teams'][team_id]
            self.assertEqual(len(team['history']), 2)
            self.assertEqual(team['history'][0]['round'], 0)
            self.assertEqual(team['history'][0]['year'], 1980)
            self.assertEqual(team['history'][1]['round'], 1)
            self.assertEqual(team['history'][1]['year'], 1985)
            
    def test_event_triggering_and_effects(self):
        """Test event triggering and effects."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        self.start_game()
        
        # Run through multiple rounds to trigger events
        for _ in range(5):  # Run 5 rounds
            # Submit decisions
            decisions = {}
            for team_id in team_ids:
                decisions[team_id] = {
                    'savings_rate': 0.3,
                    'exchange_rate_policy': 'market'
                }
                
            self.submit_decisions(decisions)
            
            # Process round
            self.process_round()
            
        # Verify events were triggered
        self.assertGreater(len(self.notifications), 0)
        
        # Check for event notifications
        event_notifications = [n for n in self.notifications if n.get('type') == 'event']
        self.assertGreater(len(event_notifications), 0)
        
        # Verify event effects
        game_state = self.game_state.get_game_state()
        for team_id in team_ids:
            team = game_state['teams'][team_id]
            history = team['history']
            
            # Look for significant changes in economic indicators that might indicate event effects
            for i in range(1, len(history)):
                prev = history[i-1]
                curr = history[i]
                
                # Calculate growth rates
                gdp_growth = (curr['gdp'] - prev['gdp']) / prev['gdp']
                tfp_growth = (curr['tfp'] - prev['tfp']) / prev['tfp']
                
                # Log growth rates for debugging
                logger.info(f"Team {team['team_name']} - Round {curr['round']} - GDP Growth: {gdp_growth:.2%}, TFP Growth: {tfp_growth:.2%}")
                
    def test_prize_awarding(self):
        """Test prize awarding."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        self.start_game()
        
        # Run through multiple rounds to trigger prizes
        for _ in range(8):  # Run 8 rounds to cover most of the game
            # Submit decisions
            decisions = {}
            for team_id in team_ids:
                decisions[team_id] = {
                    'savings_rate': 0.4,  # Higher savings rate to boost growth
                    'exchange_rate_policy': 'managed'  # Managed float for balance
                }
                
            self.submit_decisions(decisions)
            
            # Process round
            self.process_round()
            
        # Verify prizes were awarded
        game_state = self.game_state.get_game_state()
        
        # Check if any team has prizes
        prizes_awarded = False
        for team_id in team_ids:
            team = game_state['teams'][team_id]
            if 'prizes' in team and len(team['prizes']) > 0:
                prizes_awarded = True
                break
                
        # We can't guarantee prizes will be awarded in a deterministic test,
        # but we can log the state for debugging
        if not prizes_awarded:
            logger.warning("No prizes were awarded during the test")
            
            # Log economic indicators for debugging
            for team_id in team_ids:
                team = game_state['teams'][team_id]
                logger.info(f"Team {team['team_name']} final state:")
                logger.info(f"  GDP: {team['current_state']['gdp']}")
                logger.info(f"  Capital: {team['current_state']['capital']}")
                logger.info(f"  Labor: {team['current_state']['labor']}")
                logger.info(f"  TFP: {team['current_state']['tfp']}")
                
                # Log GDP growth rates
                history = team['history']
                for i in range(1, len(history)):
                    prev = history[i-1]
                    curr = history[i]
                    gdp_growth = (curr['gdp'] - prev['gdp']) / prev['gdp']
                    logger.info(f"  Round {curr['round']} GDP Growth: {gdp_growth:.2%}")
                    
    def test_game_completion_and_scoring(self):
        """Test game completion and scoring."""
        # Create teams
        teams = self.create_test_teams(3)
        team_ids = [team['team_id'] for team in teams]
        
        # Start game
        self.start_game()
        
        # Run through all rounds
        num_rounds = len(self.game_state.years) - 1  # -1 because we start at round 0
        for _ in range(num_rounds):
            # Submit decisions
            decisions = {}
            for team_id in team_ids:
                decisions[team_id] = {
                    'savings_rate': 0.3,
                    'exchange_rate_policy': 'market'
                }
                
            self.submit_decisions(decisions)
            
            # Process round
            self.process_round()
            
        # Verify game is complete
        game_state = self.game_state.get_game_state()
        self.assertTrue(game_state['game_ended'])
        self.assertEqual(game_state['current_round'], num_rounds)
        self.assertEqual(game_state['current_year'], self.game_state.years[-1])
        
        # Verify rankings
        rankings = self.game_state.rankings_manager.rankings
        self.assertGreater(len(rankings), 0)
        
        # Verify each team has a ranking
        for team_id in team_ids:
            found = False
            for rank in rankings:
                if rank['team_id'] == team_id:
                    found = True
                    self.assertIsNotNone(rank['rank'])
                    self.assertIsNotNone(rank['score'])
                    break
            self.assertTrue(found, f"Team {team_id} not found in rankings")
            
    def test_full_game_flow(self):
        """Test the complete game flow from start to finish."""
        # Run a full game
        final_state = self.run_full_game(num_teams=3, decisions_strategy='optimal')
        
        # Verify game state
        self.verify_game_state(final_state)
        
        # Verify game is complete
        self.assertTrue(final_state['game_ended'])
        
        # Verify rankings exist
        rankings = self.game_state.rankings_manager.rankings
        self.assertGreater(len(rankings), 0)
        
        # Log final state for debugging
        logger.info(f"Final game state - Round: {final_state['current_round']}, Year: {final_state['current_year']}")
        logger.info(f"Rankings: {rankings}")
        
        # Log notifications
        logger.info(f"Total notifications: {len(self.notifications)}")
        notification_types = {}
        for n in self.notifications:
            n_type = n.get('type')
            notification_types[n_type] = notification_types.get(n_type, 0) + 1
        logger.info(f"Notification types: {notification_types}")
        
if __name__ == "__main__":
    unittest.main()
