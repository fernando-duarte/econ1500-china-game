"""
Notification manager for the China Growth Game.

This module provides utilities for sending real-time notifications
to clients using Socket.IO.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Callable

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages sending real-time notifications to clients.
    
    This class provides a mock implementation for testing and can be
    extended to use actual Socket.IO in production.
    """
    
    def __init__(self):
        """Initialize the notification manager."""
        self.emitted_events = []  # For testing: track emitted events
        self.event_handlers = {}  # For testing: mock event handlers
        
    def emit(self, event: str, data: Dict[str, Any], room: Optional[str] = None) -> bool:
        """
        Emit an event to clients.
        
        Args:
            event: The event name.
            data: The event data.
            room: Optional room to emit to (e.g., team ID).
            
        Returns:
            True if the event was emitted successfully, False otherwise.
        """
        try:
            # In a real implementation, this would use socket.io to emit the event
            # For testing, we just store the event
            self.emitted_events.append({
                'event': event,
                'data': data,
                'room': room
            })
            
            # Call any registered event handlers (for testing)
            if event in self.event_handlers:
                for handler in self.event_handlers[event]:
                    handler(data, room)
                    
            logger.info(f"Emitted event {event} to {room or 'all'}")
            return True
        except Exception as e:
            logger.error(f"Error emitting event {event}: {str(e)}")
            return False
            
    def emit_prize_awarded(self, team_id: str, prize_type: str, prize_data: Dict[str, Any]) -> bool:
        """
        Emit a prize awarded event to a team.
        
        Args:
            team_id: The ID of the team that was awarded the prize.
            prize_type: The type of prize awarded.
            prize_data: The prize data.
            
        Returns:
            True if the event was emitted successfully, False otherwise.
        """
        data = {
            'team_id': team_id,
            'prize_type': prize_type,
            'prize_name': prize_data.get('name', 'Unknown Prize'),
            'prize_description': prize_data.get('description', ''),
            'effects': prize_data.get('effects', {}),
            'awarded_at': prize_data.get('awarded_at', '')
        }
        
        # Emit to the specific team
        team_room = f"team-{team_id}"
        team_success = self.emit('prizeAwarded', data, room=team_room)
        
        # Also emit to all clients (for admin/spectator views)
        all_success = self.emit('prizeAwardedGlobal', data)
        
        return team_success and all_success
        
    def emit_prizes_loaded(self, team_prizes: Dict[str, Dict[str, Dict[str, Any]]]) -> bool:
        """
        Emit a prizes loaded event to all clients.
        
        Args:
            team_prizes: Dictionary mapping team_id to prize_type to prize_data.
            
        Returns:
            True if the event was emitted successfully, False otherwise.
        """
        data = {
            'prizes': team_prizes
        }
        
        # Emit to all clients
        return self.emit('prizesLoaded', data)
        
    # For testing: register event handlers
    def on(self, event: str, handler: Callable) -> None:
        """
        Register an event handler for testing.
        
        Args:
            event: The event name.
            handler: The event handler function.
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
        
    def clear_events(self) -> None:
        """Clear all emitted events (for testing)."""
        self.emitted_events = []
        
    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all emitted events of a specific type.
        
        Args:
            event_type: Optional event type to filter by.
            
        Returns:
            List of emitted events.
        """
        if event_type is None:
            return self.emitted_events
        return [e for e in self.emitted_events if e['event'] == event_type]
