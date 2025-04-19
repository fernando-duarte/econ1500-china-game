import unittest
from economic_model_py.economic_model.game.events_manager import EventsManager

class TestEventsManager(unittest.TestCase):
    """Test cases for the EventsManager class."""

    def setUp(self):
        """Set up the test environment."""
        self.events_manager = EventsManager()
        
    def test_init(self):
        """Test the initialization of EventsManager."""
        self.assertIsInstance(self.events_manager.events, list)
        self.assertGreater(len(self.events_manager.events), 0)
        
        # Check that all events have the required fields
        for event in self.events_manager.events:
            self.assertIn("year", event)
            self.assertIn("name", event)
            self.assertIn("description", event)
            self.assertIn("effects", event)
            self.assertIn("triggered", event)
            self.assertFalse(event["triggered"])
            
        # Check that specific required events are present
        event_names = [event["name"] for event in self.events_manager.events]
        self.assertIn("China Joins WTO", event_names)
        self.assertIn("Global Financial Crisis", event_names)
        self.assertIn("US-China Trade War", event_names)
        self.assertIn("COVID-19 Pandemic", event_names)
        
        # Check event years
        wto_event = next(e for e in self.events_manager.events if e["name"] == "China Joins WTO")
        gfc_event = next(e for e in self.events_manager.events if e["name"] == "Global Financial Crisis")
        covid_event = next(e for e in self.events_manager.events if e["name"] == "COVID-19 Pandemic")
        
        self.assertEqual(wto_event["year"], 2001)
        self.assertEqual(gfc_event["year"], 2008)
        self.assertEqual(covid_event["year"], 2020)
        
    def test_get_current_events(self):
        """Test event retrieval for the current year."""
        # No events in 1980
        events_1980 = self.events_manager.get_current_events(1980)
        self.assertEqual(len(events_1980), 0)
        
        # WTO event in 2001
        events_2001 = self.events_manager.get_current_events(2001)
        self.assertEqual(len(events_2001), 1)
        self.assertEqual(events_2001[0]["name"], "China Joins WTO")
        self.assertTrue(events_2001[0]["triggered"])
        
        # Check that the event is not triggered again
        events_2001_again = self.events_manager.get_current_events(2001)
        self.assertEqual(len(events_2001_again), 0)
        
        # GFC event in 2008
        events_2008 = self.events_manager.get_current_events(2008)
        self.assertEqual(len(events_2008), 1)
        self.assertEqual(events_2008[0]["name"], "Global Financial Crisis")
        
        # COVID event in 2020
        events_2020 = self.events_manager.get_current_events(2020)
        self.assertEqual(len(events_2020), 1)
        self.assertEqual(events_2020[0]["name"], "COVID-19 Pandemic")
        
    def test_reset_events(self):
        """Test event reset."""
        # Trigger some events
        self.events_manager.get_current_events(2001)
        self.events_manager.get_current_events(2008)
        
        # Check that they are triggered
        wto_event = next(e for e in self.events_manager.events if e["name"] == "China Joins WTO")
        gfc_event = next(e for e in self.events_manager.events if e["name"] == "Global Financial Crisis")
        self.assertTrue(wto_event["triggered"])
        self.assertTrue(gfc_event["triggered"])
        
        # Reset events
        self.events_manager.reset_events()
        
        # Check that they are no longer triggered
        wto_event = next(e for e in self.events_manager.events if e["name"] == "China Joins WTO")
        gfc_event = next(e for e in self.events_manager.events if e["name"] == "Global Financial Crisis")
        self.assertFalse(wto_event["triggered"])
        self.assertFalse(gfc_event["triggered"])
        
        # Check that they can be triggered again
        events_2001 = self.events_manager.get_current_events(2001)
        self.assertEqual(len(events_2001), 1)
        self.assertEqual(events_2001[0]["name"], "China Joins WTO")
        
    def test_event_effects(self):
        """Test that events have the correct effects."""
        # WTO event should have TFP and exports effects
        wto_event = next(e for e in self.events_manager.events if e["name"] == "China Joins WTO")
        self.assertIn("tfp_increase", wto_event["effects"])
        self.assertIn("exports_multiplier", wto_event["effects"])
        self.assertGreater(wto_event["effects"]["tfp_increase"], 0)
        self.assertGreater(wto_event["effects"]["exports_multiplier"], 1)
        
        # GFC event should have negative GDP growth effect
        gfc_event = next(e for e in self.events_manager.events if e["name"] == "Global Financial Crisis")
        self.assertIn("gdp_growth_delta", gfc_event["effects"])
        self.assertLess(gfc_event["effects"]["gdp_growth_delta"], 0)
        
        # COVID event should have negative GDP growth effect
        covid_event = next(e for e in self.events_manager.events if e["name"] == "COVID-19 Pandemic")
        self.assertIn("gdp_growth_delta", covid_event["effects"])
        self.assertLess(covid_event["effects"]["gdp_growth_delta"], 0)

if __name__ == '__main__':
    unittest.main()
