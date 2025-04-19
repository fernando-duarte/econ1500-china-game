import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
from china_growth_game.economic_model.game.prize_manager import PrizeManager, PRIZE_TYPES

class TestPrizeManager(unittest.TestCase):
    """Test cases for the PrizeManager class."""

    def setUp(self):
        """Set up the test environment."""
        self.prize_manager = PrizeManager()
        
        # Create mock teams for testing
        self.mock_teams = {
            "team1": {
                "team_id": "team1",
                "team_name": "Team 1",
                "eliminated": False,
                "current_state": {
                    "Y": 1000,
                    "GDP": 1000,
                    "NX": 100,
                    "C": 700,
                    "A": 1.5
                },
                "history": [
                    {"Y": 800, "GDP": 800},
                    {"Y": 880, "GDP": 880},  # 10% growth
                    {"Y": 968, "GDP": 968},  # 10% growth
                    {"Y": 1000, "GDP": 1000}  # ~3.3% growth
                ]
            },
            "team2": {
                "team_id": "team2",
                "team_name": "Team 2",
                "eliminated": False,
                "current_state": {
                    "Y": 1200,
                    "GDP": 1200,
                    "NX": 50,
                    "C": 900,
                    "A": 1.8
                },
                "history": [
                    {"Y": 900, "GDP": 900},
                    {"Y": 990, "GDP": 990},  # 10% growth
                    {"Y": 1089, "GDP": 1089},  # 10% growth
                    {"Y": 1200, "GDP": 1200}  # ~10.2% growth
                ]
            },
            "team3": {
                "team_id": "team3",
                "team_name": "Team 3",
                "eliminated": False,
                "current_state": {
                    "Y": 800,
                    "GDP": 800,
                    "NX": 150,
                    "C": 500,
                    "A": 1.2
                },
                "history": [
                    {"Y": 700, "GDP": 700},
                    {"Y": 650, "GDP": 650},  # -7.1% growth (negative)
                    {"Y": 700, "GDP": 700},  # 7.7% growth (recovery)
                    {"Y": 800, "GDP": 800}  # 14.3% growth
                ]
            },
            "team4": {
                "team_id": "team4",
                "team_name": "Team 4",
                "eliminated": True,  # This team is eliminated
                "current_state": {
                    "Y": 500,
                    "GDP": 500,
                    "NX": 20,
                    "C": 400,
                    "A": 1.0
                },
                "history": []
            }
        }
        
        # Mock rankings
        self.mock_rankings = {
            "gdp": ["team2", "team1", "team3"],
            "net_exports": ["team3", "team1", "team2"],
            "balanced_economy": ["team2", "team1", "team3"]
        }
        
    def test_init(self):
        """Test the initialization of PrizeManager."""
        self.assertIsInstance(self.prize_manager.awarded_prizes, dict)
        self.assertEqual(len(self.prize_manager.awarded_prizes), 0)
        
    def test_check_prize_eligibility(self):
        """Test prize eligibility checking."""
        # Test with round < 3 (should return empty dict)
        eligible_prizes = self.prize_manager.check_prize_eligibility(
            self.mock_teams, 2, 1990, self.mock_rankings
        )
        self.assertEqual(len(eligible_prizes), 0)
        
        # Test with round >= 3
        eligible_prizes = self.prize_manager.check_prize_eligibility(
            self.mock_teams, 3, 1995, self.mock_rankings
        )
        
        # team2 should be eligible for GDP growth achievement (3 consecutive rounds > 8%)
        self.assertIn("team2", eligible_prizes)
        prize_types = [prize["type"] for prize in eligible_prizes.get("team2", [])]
        self.assertIn("gdp_growth", prize_types)
        
        # team2 should be eligible for tech leadership (highest TFP)
        self.assertIn("tech_leadership", prize_types)
        
        # team2 should be eligible for sustainable growth (top in balanced economy)
        self.assertIn("sustainable_growth", prize_types)
        
        # team3 should be eligible for crisis management (recovery from negative growth)
        self.assertIn("team3", eligible_prizes)
        prize_types = [prize["type"] for prize in eligible_prizes.get("team3", [])]
        self.assertIn("crisis_management", prize_types)
        
        # team3 should be eligible for export champion (top in net exports)
        self.assertIn("export_champion", prize_types)
        
        # team4 is eliminated and should not be eligible for any prizes
        self.assertNotIn("team4", eligible_prizes)
        
    def test_award_prizes(self):
        """Test prize awarding."""
        # Create eligible prizes dict
        eligible_prizes = {
            "team1": [
                {
                    "type": "gdp_growth",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            ],
            "team2": [
                {
                    "type": "tech_leadership",
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                },
                {
                    "type": "sustainable_growth",
                    "name": PRIZE_TYPES["sustainable_growth"]["name"],
                    "description": PRIZE_TYPES["sustainable_growth"]["description"],
                    "effects": PRIZE_TYPES["sustainable_growth"]["effects"]
                }
            ]
        }
        
        # Award prizes
        awarded = self.prize_manager.award_prizes(eligible_prizes)
        
        # Check that prizes were awarded
        self.assertIn("team1", awarded)
        self.assertIn("team2", awarded)
        self.assertEqual(len(awarded["team1"]), 1)
        self.assertEqual(len(awarded["team2"]), 2)
        
        # Check that prizes are stored in the manager
        self.assertIn("team1", self.prize_manager.awarded_prizes)
        self.assertIn("team2", self.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", self.prize_manager.awarded_prizes["team1"])
        self.assertIn("tech_leadership", self.prize_manager.awarded_prizes["team2"])
        self.assertIn("sustainable_growth", self.prize_manager.awarded_prizes["team2"])
        
        # Check prize details
        self.assertIn("awarded_at", self.prize_manager.awarded_prizes["team1"]["gdp_growth"])
        self.assertIn("name", self.prize_manager.awarded_prizes["team1"]["gdp_growth"])
        self.assertIn("description", self.prize_manager.awarded_prizes["team1"]["gdp_growth"])
        self.assertIn("effects", self.prize_manager.awarded_prizes["team1"]["gdp_growth"])
        
    def test_prize_idempotency(self):
        """Test that prizes can only be awarded once per team per game."""
        # Create eligible prizes dict
        eligible_prizes = {
            "team1": [
                {
                    "type": "gdp_growth",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            ]
        }
        
        # Award prizes first time
        awarded1 = self.prize_manager.award_prizes(eligible_prizes)
        self.assertIn("team1", awarded1)
        self.assertEqual(len(awarded1["team1"]), 1)
        
        # Try to award the same prize again
        awarded2 = self.prize_manager.award_prizes(eligible_prizes)
        self.assertEqual(len(awarded2), 0)  # No prizes should be awarded
        
        # Check that only one prize was stored
        self.assertEqual(len(self.prize_manager.awarded_prizes["team1"]), 1)
        
    def test_apply_prize_effects(self):
        """Test applying prize effects to round results."""
        # Award some prizes first
        self.prize_manager.awarded_prizes = {
            "team1": {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            },
            "team2": {
                "tech_leadership": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                },
                "export_champion": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["export_champion"]["name"],
                    "description": PRIZE_TYPES["export_champion"]["description"],
                    "effects": PRIZE_TYPES["export_champion"]["effects"]
                }
            }
        }
        
        # Test round results for team1 (has gdp_growth prize)
        round_results1 = {
            "A_next": 1.5,
            "Y_t": 1000,
            "NX_t": 100,
            "C_t": 700
        }
        
        modified_results1 = self.prize_manager.apply_prize_effects("team1", round_results1)
        
        # Check that TFP was boosted by 5%
        self.assertAlmostEqual(modified_results1["A_next"], 1.5 * 1.05)
        
        # Test round results for team2 (has tech_leadership and export_champion prizes)
        round_results2 = {
            "A_next": 1.8,
            "Y_t": 1200,
            "NX_t": 50,
            "C_t": 900,
            "fdi_ratio": 0.1
        }
        
        modified_results2 = self.prize_manager.apply_prize_effects("team2", round_results2)
        
        # Check that FDI ratio was boosted by 10%
        self.assertAlmostEqual(modified_results2["fdi_ratio"], 0.1 * 1.1)
        
        # Check that net exports were boosted by 10%
        self.assertAlmostEqual(modified_results2["NX_t"], 50 * 1.1)
        
        # Test team with no prizes
        round_results3 = {
            "A_next": 1.2,
            "Y_t": 800,
            "NX_t": 150,
            "C_t": 500
        }
        
        modified_results3 = self.prize_manager.apply_prize_effects("team3", round_results3)
        
        # Results should be unchanged
        self.assertEqual(modified_results3, round_results3)
        
    def test_get_team_prizes(self):
        """Test getting prizes for a specific team."""
        # Award some prizes first
        self.prize_manager.awarded_prizes = {
            "team1": {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            },
            "team2": {
                "tech_leadership": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                }
            }
        }
        
        # Get prizes for team1
        team1_prizes = self.prize_manager.get_team_prizes("team1")
        self.assertEqual(len(team1_prizes), 1)
        self.assertIn("gdp_growth", team1_prizes)
        
        # Get prizes for team2
        team2_prizes = self.prize_manager.get_team_prizes("team2")
        self.assertEqual(len(team2_prizes), 1)
        self.assertIn("tech_leadership", team2_prizes)
        
        # Get prizes for team with no prizes
        team3_prizes = self.prize_manager.get_team_prizes("team3")
        self.assertEqual(len(team3_prizes), 0)
        
    def test_get_all_prizes(self):
        """Test getting all awarded prizes."""
        # Award some prizes first
        self.prize_manager.awarded_prizes = {
            "team1": {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            },
            "team2": {
                "tech_leadership": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                }
            }
        }
        
        # Get all prizes
        all_prizes = self.prize_manager.get_all_prizes()
        self.assertEqual(len(all_prizes), 2)
        self.assertIn("team1", all_prizes)
        self.assertIn("team2", all_prizes)
        self.assertIn("gdp_growth", all_prizes["team1"])
        self.assertIn("tech_leadership", all_prizes["team2"])
        
    def test_reset_prizes(self):
        """Test resetting all awarded prizes."""
        # Award some prizes first
        self.prize_manager.awarded_prizes = {
            "team1": {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Reset prizes
        self.prize_manager.reset_prizes()
        
        # Check that prizes were reset
        self.assertEqual(len(self.prize_manager.awarded_prizes), 0)
        
    def test_prize_concurrency(self):
        """Test that multiple teams can receive the same prize type if eligible."""
        # Create eligible prizes dict with multiple teams eligible for the same prize
        eligible_prizes = {
            "team1": [
                {
                    "type": "gdp_growth",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            ],
            "team2": [
                {
                    "type": "gdp_growth",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            ]
        }
        
        # Award prizes
        awarded = self.prize_manager.award_prizes(eligible_prizes)
        
        # Check that both teams received the prize
        self.assertIn("team1", awarded)
        self.assertIn("team2", awarded)
        self.assertEqual(len(awarded["team1"]), 1)
        self.assertEqual(len(awarded["team2"]), 1)
        
        # Check that prizes are stored in the manager
        self.assertIn("team1", self.prize_manager.awarded_prizes)
        self.assertIn("team2", self.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", self.prize_manager.awarded_prizes["team1"])
        self.assertIn("gdp_growth", self.prize_manager.awarded_prizes["team2"])
        
    def test_prize_effect_stacking(self):
        """Test that multiple prize effects stack properly."""
        # Award multiple prizes to a team
        self.prize_manager.awarded_prizes = {
            "team1": {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                },
                "sustainable_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["sustainable_growth"]["name"],
                    "description": PRIZE_TYPES["sustainable_growth"]["description"],
                    "effects": PRIZE_TYPES["sustainable_growth"]["effects"]
                }
            }
        }
        
        # Test round results for team1 (has gdp_growth and sustainable_growth prizes)
        round_results = {
            "A_next": 1.5,
            "Y_t": 1000,
            "NX_t": 100,
            "C_t": 700
        }
        
        modified_results = self.prize_manager.apply_prize_effects("team1", round_results)
        
        # Check that TFP was boosted by 5% (from gdp_growth)
        self.assertAlmostEqual(modified_results["A_next"], 1.5 * 1.05)
        
        # Check that consumption was boosted by 10% (from sustainable_growth)
        self.assertAlmostEqual(modified_results["C_t"], 700 * 1.1)
        
    def test_shock_resistance_effect(self):
        """Test the shock resistance effect from the crisis management prize."""
        # Award crisis management prize to a team
        self.prize_manager.awarded_prizes = {
            "team1": {
                "crisis_management": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["crisis_management"]["name"],
                    "description": PRIZE_TYPES["crisis_management"]["description"],
                    "effects": PRIZE_TYPES["crisis_management"]["effects"]
                }
            }
        }
        
        # Test round results with a negative GDP shock
        round_results = {
            "A_next": 1.5,
            "Y_t": 1000,
            "NX_t": 100,
            "C_t": 700,
            "gdp_growth_delta": -0.05  # 5% negative shock
        }
        
        modified_results = self.prize_manager.apply_prize_effects("team1", round_results)
        
        # Check that the negative shock was reduced by 15%
        # Original: -0.05, with 15% reduction: -0.05 * (1 - 0.15) = -0.0425
        self.assertAlmostEqual(modified_results["gdp_growth_delta"], -0.05 * 0.85)
        
        # Test that positive shocks are not affected
        round_results = {
            "A_next": 1.5,
            "Y_t": 1000,
            "NX_t": 100,
            "C_t": 700,
            "gdp_growth_delta": 0.05  # 5% positive shock
        }
        
        modified_results = self.prize_manager.apply_prize_effects("team1", round_results)
        
        # Check that the positive shock was not affected
        self.assertAlmostEqual(modified_results["gdp_growth_delta"], 0.05)

if __name__ == '__main__':
    unittest.main()
