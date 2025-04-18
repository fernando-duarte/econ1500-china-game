import unittest
from constants import (
    DEFAULT_SAVINGS_RATE,
    DEFAULT_EXCHANGE_RATE_POLICY,
    DEFAULT_INITIAL_CONDITIONS,
    EXCHANGE_RATE_POLICIES,
    POLICY_MULTIPLIERS,
    DEFAULT_YEARS,
    MAX_ROUNDS,
    WTO_EVENT_YEAR,
    GFC_EVENT_YEAR,
    COVID_EVENT_YEAR
)

class TestConstants(unittest.TestCase):
    """Test cases for the constants module."""

    def test_default_savings_rate(self):
        """Test the default savings rate."""
        self.assertIsInstance(DEFAULT_SAVINGS_RATE, float)
        self.assertGreater(DEFAULT_SAVINGS_RATE, 0)
        self.assertLess(DEFAULT_SAVINGS_RATE, 1)
        
    def test_default_exchange_rate_policy(self):
        """Test the default exchange rate policy."""
        self.assertIsInstance(DEFAULT_EXCHANGE_RATE_POLICY, str)
        self.assertIn(DEFAULT_EXCHANGE_RATE_POLICY, EXCHANGE_RATE_POLICIES)
        
    def test_default_initial_conditions(self):
        """Test the default initial conditions."""
        self.assertIsInstance(DEFAULT_INITIAL_CONDITIONS, dict)
        self.assertIn('Y', DEFAULT_INITIAL_CONDITIONS)
        self.assertIn('K', DEFAULT_INITIAL_CONDITIONS)
        self.assertIn('L', DEFAULT_INITIAL_CONDITIONS)
        self.assertIn('H', DEFAULT_INITIAL_CONDITIONS)
        self.assertIn('A', DEFAULT_INITIAL_CONDITIONS)
        
        # Check that values are reasonable
        self.assertGreater(DEFAULT_INITIAL_CONDITIONS['Y'], 0)
        self.assertGreater(DEFAULT_INITIAL_CONDITIONS['K'], 0)
        self.assertGreater(DEFAULT_INITIAL_CONDITIONS['L'], 0)
        self.assertGreater(DEFAULT_INITIAL_CONDITIONS['H'], 0)
        self.assertGreater(DEFAULT_INITIAL_CONDITIONS['A'], 0)
        
    def test_exchange_rate_policies(self):
        """Test the exchange rate policies."""
        self.assertIsInstance(EXCHANGE_RATE_POLICIES, list)
        self.assertGreater(len(EXCHANGE_RATE_POLICIES), 0)
        self.assertIn('market', EXCHANGE_RATE_POLICIES)
        self.assertIn('undervalue', EXCHANGE_RATE_POLICIES)
        self.assertIn('overvalue', EXCHANGE_RATE_POLICIES)
        
    def test_policy_multipliers(self):
        """Test the policy multipliers."""
        self.assertIsInstance(POLICY_MULTIPLIERS, dict)
        
        # Check that all policies have multipliers
        for policy in EXCHANGE_RATE_POLICIES:
            self.assertIn(policy, POLICY_MULTIPLIERS)
            self.assertIsInstance(POLICY_MULTIPLIERS[policy], (int, float))
            
        # Check specific multiplier relationships
        self.assertGreater(POLICY_MULTIPLIERS['undervalue'], POLICY_MULTIPLIERS['market'])
        self.assertLess(POLICY_MULTIPLIERS['overvalue'], POLICY_MULTIPLIERS['market'])
        self.assertEqual(POLICY_MULTIPLIERS['market'], 1.0)
        
    def test_default_years(self):
        """Test the default years."""
        self.assertIsInstance(DEFAULT_YEARS, list)
        self.assertGreater(len(DEFAULT_YEARS), 0)
        self.assertEqual(DEFAULT_YEARS[0], 1980)
        self.assertEqual(DEFAULT_YEARS[-1], 2025)
        
        # Check that years are in 5-year increments
        for i in range(1, len(DEFAULT_YEARS)):
            self.assertEqual(DEFAULT_YEARS[i] - DEFAULT_YEARS[i-1], 5)
            
    def test_max_rounds(self):
        """Test the maximum number of rounds."""
        self.assertIsInstance(MAX_ROUNDS, int)
        self.assertGreater(MAX_ROUNDS, 0)
        self.assertEqual(MAX_ROUNDS, 10)  # Should match the number of 5-year periods from 1980 to 2025
        
    def test_event_years(self):
        """Test the event years."""
        self.assertIsInstance(WTO_EVENT_YEAR, int)
        self.assertIsInstance(GFC_EVENT_YEAR, int)
        self.assertIsInstance(COVID_EVENT_YEAR, int)
        
        # Check that event years are in chronological order
        self.assertLess(WTO_EVENT_YEAR, GFC_EVENT_YEAR)
        self.assertLess(GFC_EVENT_YEAR, COVID_EVENT_YEAR)
        
        # Check specific event years
        self.assertEqual(WTO_EVENT_YEAR, 2000)
        self.assertEqual(GFC_EVENT_YEAR, 2010)
        self.assertEqual(COVID_EVENT_YEAR, 2020)

if __name__ == '__main__':
    unittest.main()
