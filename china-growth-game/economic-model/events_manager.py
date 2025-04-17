from typing import Dict, List, Any

class EventsManager:
    """
    Manages economic events that occur during the game.
    """
    
    def __init__(self):
        self.events = self._initialize_events()
        
    def _initialize_events(self) -> List[Dict[str, Any]]:
        """Initialize economic events that will occur during the game."""
        return [
            {
                "year": 2001,
                "name": "China Joins WTO",
                "description": "China joins the World Trade Organization",
                "effects": {
                    "exports_multiplier": 1.25,
                    "tfp_increase": 0.02
                },
                "triggered": False
            },
            {
                "year": 2008,
                "name": "Global Financial Crisis",
                "description": "Global financial markets collapse",
                "effects": {
                    "exports_multiplier": 0.8,
                    "gdp_growth_delta": -0.03
                },
                "triggered": False
            },
            {
                "year": 2018,
                "name": "US-China Trade War",
                "description": "Escalating tariffs between the US and China",
                "effects": {
                    "exports_multiplier": 0.9
                },
                "triggered": False
            },
            {
                "year": 2020,
                "name": "COVID-19 Pandemic",
                "description": "Global pandemic disrupts economies",
                "effects": {
                    "gdp_growth_delta": -0.04
                },
                "triggered": False
            }
        ]
    
    def get_current_events(self, current_year: int) -> List[Dict[str, Any]]:
        """Get events that should be triggered in the current year."""
        current_events = []
        for event in self.events:
            if event["year"] == current_year and not event["triggered"]:
                event["triggered"] = True
                current_events.append(event)
        return current_events
    
    def reset_events(self):
        """Reset all events to non-triggered state."""
        for event in self.events:
            event["triggered"] = False 