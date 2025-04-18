import unittest
import numpy as np
from china_growth_game.economic_model.core.solow_core import (
    calculate_production,
    calculate_capital_next,
    calculate_labor_next,
    calculate_human_capital_next,
    calculate_tfp_next,
    calculate_exchange_rate,
    calculate_foreign_income,
    calculate_net_exports,
    get_default_parameters,
    calculate_openness_ratio,
    calculate_fdi_ratio,
    solve_solow_model
)

class TestSolowCore(unittest.TestCase):
    """Test cases for the core economic functions in solow_core.py."""

    def setUp(self):
        """Set up the test environment."""
        self.default_params = get_default_parameters()

    def test_calculate_production(self):
        """Test the Cobb-Douglas production function."""
        # Test with standard values
        A, K, L, H, alpha = 1.0, 100.0, 50.0, 2.0, 0.3
        Y = calculate_production(A, K, L, H, alpha)
        self.assertGreater(Y, 0, "Production should be positive")

        # Test with zero capital (should return 0)
        Y_zero_K = calculate_production(A, 0, L, H, alpha)
        self.assertEqual(Y_zero_K, 0, "Production with zero capital should be 0")

        # Test with negative capital (should handle gracefully and return 0)
        Y_neg_K = calculate_production(A, -10, L, H, alpha)
        self.assertEqual(Y_neg_K, 0, "Production with negative capital should be 0")

        # Test with different alpha values
        Y_high_alpha = calculate_production(A, K, L, H, 0.5)
        Y_low_alpha = calculate_production(A, K, L, H, 0.1)
        self.assertNotEqual(Y_high_alpha, Y_low_alpha, "Different alpha should yield different output")

    def test_calculate_capital_next(self):
        """Test the capital accumulation function."""
        # Test with standard values
        K, Y, NX, s, delta = 100.0, 50.0, 5.0, 0.2, 0.1
        K_next, I = calculate_capital_next(K, Y, NX, s, delta)

        # Investment should be s*Y + NX
        self.assertAlmostEqual(I, s*Y + NX, places=5, msg="Investment should be s*Y + NX")

        # K_next should be (1-delta)*K + I
        self.assertAlmostEqual(K_next, (1-delta)*K + I, places=5, msg="K_next should be (1-delta)*K + I")

        # Test with negative net exports
        K_next_neg_NX, I_neg_NX = calculate_capital_next(K, Y, -10.0, s, delta)
        self.assertLess(I_neg_NX, I, "Investment should be lower with negative net exports")

        # Test with very negative net exports (causing negative investment)
        K_next_very_neg_NX, I_very_neg_NX = calculate_capital_next(K, Y, -20.0, s, delta)
        self.assertGreaterEqual(K_next_very_neg_NX, 0, "K_next should not be negative")

    def test_calculate_labor_next(self):
        """Test the labor force growth function."""
        L = 100.0
        n = 0.01  # 1% growth rate

        L_next = calculate_labor_next(L, n)
        self.assertAlmostEqual(L_next, L * (1 + n), places=5, msg="L_next should be L * (1 + n)")

        # Test with negative growth rate
        L_next_neg = calculate_labor_next(L, -0.01)
        self.assertLess(L_next_neg, L, "L_next should decrease with negative growth rate")

    def test_calculate_human_capital_next(self):
        """Test the human capital growth function."""
        H = 2.0
        eta = 0.02  # 2% growth rate

        H_next = calculate_human_capital_next(H, eta)
        self.assertAlmostEqual(H_next, H * (1 + eta), places=5, msg="H_next should be H * (1 + eta)")

        # Test with negative growth rate
        H_next_neg = calculate_human_capital_next(H, -0.01)
        self.assertLess(H_next_neg, H, "H_next should decrease with negative growth rate")

    def test_calculate_tfp_next(self):
        """Test the TFP growth function."""
        A = 1.0
        g = 0.005  # Base productivity growth
        theta = 0.1  # Effect of openness
        openness_ratio = 0.2
        phi = 0.1  # Effect of FDI
        fdi_ratio = 0.05

        A_next = calculate_tfp_next(A, g, theta, openness_ratio, phi, fdi_ratio)
        expected_A_next = A * (1 + g + theta * openness_ratio + phi * fdi_ratio)
        self.assertAlmostEqual(A_next, expected_A_next, places=5,
                              msg="A_next should be A * (1 + g + theta*openness + phi*fdi)")

        # Test with zero openness and FDI
        A_next_base = calculate_tfp_next(A, g, theta, 0, phi, 0)
        self.assertAlmostEqual(A_next_base, A * (1 + g), places=5,
                              msg="A_next should be A * (1 + g) with zero openness and FDI")

    def test_calculate_exchange_rate(self):
        """Test the exchange rate calculation function."""
        year = 2000

        # Test different policies
        e_market = calculate_exchange_rate(year, 'market')
        e_undervalue = calculate_exchange_rate(year, 'undervalue')
        e_overvalue = calculate_exchange_rate(year, 'overvalue')

        self.assertGreater(e_undervalue, e_market, "Undervalued exchange rate should be higher than market")
        self.assertLess(e_overvalue, e_market, "Overvalued exchange rate should be lower than market")

        # Test invalid policy
        with self.assertRaises(ValueError):
            calculate_exchange_rate(year, 'invalid_policy')

    def test_calculate_foreign_income(self):
        """Test the foreign income calculation function."""
        # Test for different years
        Y_star_1980 = calculate_foreign_income(1980)
        Y_star_2000 = calculate_foreign_income(2000)
        Y_star_2020 = calculate_foreign_income(2020)

        self.assertLess(Y_star_1980, Y_star_2000, "Foreign income should increase over time")
        self.assertLess(Y_star_2000, Y_star_2020, "Foreign income should increase over time")

    def test_calculate_net_exports(self):
        """Test the net exports calculation function."""
        Y_t = 1000.0
        Y_1980 = 500.0
        e_t = 1.0
        E_1980 = 1.0
        Y_star_t = 2000.0
        Y_STAR_1980 = 1000.0
        X0 = 20.0
        M0 = 15.0
        epsilon_x = 1.5
        epsilon_m = 1.2
        mu_x = 1.0
        mu_m = 1.0

        NX = calculate_net_exports(
            Y_t, Y_1980, e_t, E_1980, Y_star_t, Y_STAR_1980,
            X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
        )

        self.assertIsInstance(NX, float, "Net exports should be a float")

        # Test with different exchange rates
        NX_high_e = calculate_net_exports(
            Y_t, Y_1980, 1.2, E_1980, Y_star_t, Y_STAR_1980,
            X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
        )

        NX_low_e = calculate_net_exports(
            Y_t, Y_1980, 0.8, E_1980, Y_star_t, Y_STAR_1980,
            X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
        )

        self.assertGreater(NX_high_e, NX_low_e,
                          "Net exports should be higher with a higher exchange rate")

    def test_calculate_openness_ratio(self):
        """Test the openness ratio calculation function."""
        # Test for different round indices
        openness_0 = calculate_openness_ratio(0)
        openness_5 = calculate_openness_ratio(5)

        self.assertLess(openness_0, openness_5, "Openness ratio should increase with round index")

        # Test negative round index (should handle gracefully)
        openness_neg = calculate_openness_ratio(-1)
        self.assertEqual(openness_neg, openness_0, "Negative round index should be treated as 0")

    def test_calculate_fdi_ratio(self):
        """Test the FDI ratio calculation function."""
        # Test for different years
        fdi_1980 = calculate_fdi_ratio(1980)
        fdi_2000 = calculate_fdi_ratio(2000)

        self.assertGreaterEqual(fdi_2000, fdi_1980, "FDI ratio should not decrease over time")

    def test_solve_solow_model(self):
        """Test the full Solow model solution function."""
        # Set up parameters for a simple simulation
        initial_year = 1980
        initial_conditions = {
            'Y': 500.0,
            'K': 1000.0,
            'L': 100.0,
            'H': 1.0,
            'A': 1.0
        }
        parameters = self.default_params.copy()
        parameters['s'] = 0.2  # Set savings rate for simulation
        years = np.array([1980, 1985, 1990])

        # Run the simulation
        results = solve_solow_model(initial_year, initial_conditions, parameters, years)

        # Check that the results DataFrame has the expected structure
        import pandas as pd
        self.assertIsInstance(results, pd.DataFrame, "Results should be a pandas DataFrame")
        self.assertEqual(len(results), len(years), "Results should have one row per year")

        # Check that key variables are present and have reasonable values
        # GDP should be positive and generally increasing
        self.assertTrue(all(results['GDP'] > 0), "GDP should be positive")

        # Capital should be positive
        self.assertTrue(all(results['Capital'] > 0), "Capital should be positive")

        # Labor force should be positive and increasing
        self.assertTrue(all(results['Labor Force'] > 0), "Labor force should be positive")
        self.assertTrue(results['Labor Force'].is_monotonic_increasing, "Labor force should be increasing")

        # Human capital should be positive and increasing
        self.assertTrue(all(results['Human Capital'] > 0), "Human capital should be positive")
        self.assertTrue(results['Human Capital'].is_monotonic_increasing, "Human capital should be increasing")

        # TFP should be positive and increasing
        self.assertTrue(all(results['Productivity (TFP)'] > 0), "TFP should be positive")
        self.assertTrue(results['Productivity (TFP)'].is_monotonic_increasing, "TFP should be increasing")

if __name__ == '__main__':
    unittest.main()
