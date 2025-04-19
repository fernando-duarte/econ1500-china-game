"""
Persistence utilities for the China Growth Game.

This module provides utilities for persisting game state to a database
or file system.
"""

import os
import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Thread-local storage for database connections
_local = threading.local()

class PersistenceManager:
    """
    Manages persistence of game state to a database or file system.

    This implementation uses SQLite for simplicity, but could be extended
    to use other databases like PostgreSQL or MongoDB.
    """

    def __init__(self, db_path: str = None, data_dir: str = None):
        """
        Initialize the persistence manager.

        Args:
            db_path: Path to the SQLite database file. If None, uses a default path.
            data_dir: Directory to store data files. If provided, db_path will be set to a file in this directory.
        """
        if data_dir is not None:
            # Use the provided data directory
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, 'game_state.db')
        elif db_path is not None:
            # Use the provided database path
            self.db_path = db_path
        else:
            # Use a default path in the current directory
            self.db_path = os.path.join(os.getcwd(), 'game_state.db')

        # Initialize the database
        self._init_db()

    def _get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(_local, 'connection'):
            _local.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            _local.connection.execute('PRAGMA foreign_keys = ON')
            # Use Row factory for better column access
            _local.connection.row_factory = sqlite3.Row
        return _local.connection

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create games table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            current_round INTEGER NOT NULL,
            current_year INTEGER NOT NULL,
            game_started INTEGER NOT NULL,
            game_ended INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')

        # Create teams table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id TEXT PRIMARY KEY,
            game_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            eliminated INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
        ''')

        # Create prizes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prizes (
            prize_id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            game_id TEXT NOT NULL,
            prize_type TEXT NOT NULL,
            prize_name TEXT NOT NULL,
            prize_description TEXT NOT NULL,
            awarded_at TEXT NOT NULL,
            effects TEXT NOT NULL,
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
        ''')

        conn.commit()

    def save_game_state(self, game_state: Dict[str, Any]) -> bool:
        """
        Save the game state to the database.

        Args:
            game_state: The game state to save.

        Returns:
            True if successful, False otherwise.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Extract game data
            game_id = game_state.get('game_id')
            created_at = game_state.get('created_at')
            current_round = game_state.get('current_round', 0)
            current_year = game_state.get('current_year', 1980)
            game_started = 1 if game_state.get('game_started', False) else 0
            game_ended = 1 if game_state.get('game_ended', False) else 0
            updated_at = datetime.now().isoformat()

            # Insert or update game
            cursor.execute('''
            INSERT OR REPLACE INTO games
            (game_id, created_at, current_round, current_year, game_started, game_ended, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (game_id, created_at, current_round, current_year, game_started, game_ended, updated_at))

            # Save teams
            teams = game_state.get('teams', {})
            for team_id, team_data in teams.items():
                team_name = team_data.get('team_name', f'Team {team_id}')
                team_created_at = team_data.get('created_at', created_at)
                eliminated = 1 if team_data.get('eliminated', False) else 0

                cursor.execute('''
                INSERT OR REPLACE INTO teams
                (team_id, game_id, team_name, created_at, eliminated)
                VALUES (?, ?, ?, ?, ?)
                ''', (team_id, game_id, team_name, team_created_at, eliminated))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving game state: {str(e)}")
            conn.rollback()
            return False

    def save_prizes(self, game_id: str, prizes: Dict[str, Dict[str, Dict[str, Any]]]) -> bool:
        """
        Save prizes to the database.

        Args:
            game_id: The ID of the game.
            prizes: Dictionary mapping team_id to prize_type to prize_data.

        Returns:
            True if successful, False otherwise.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # First, delete existing prizes for this game
            cursor.execute('DELETE FROM prizes WHERE game_id = ?', (game_id,))

            # Insert new prizes
            for team_id, team_prizes in prizes.items():
                for prize_type, prize_data in team_prizes.items():
                    prize_id = f"{game_id}_{team_id}_{prize_type}"
                    prize_name = prize_data.get('name', 'Unknown Prize')
                    prize_description = prize_data.get('description', '')
                    awarded_at = prize_data.get('awarded_at', datetime.now().isoformat())
                    effects = json.dumps(prize_data.get('effects', {}))

                    cursor.execute('''
                    INSERT INTO prizes
                    (prize_id, team_id, game_id, prize_type, prize_name, prize_description, awarded_at, effects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (prize_id, team_id, game_id, prize_type, prize_name, prize_description, awarded_at, effects))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving prizes: {str(e)}")
            conn.rollback()
            return False

    def load_prizes(self, game_id: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load prizes from the database.

        Args:
            game_id: The ID of the game.

        Returns:
            Dictionary mapping team_id to prize_type to prize_data.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM prizes WHERE game_id = ?
            ''', (game_id,))

            rows = cursor.fetchall()
            prizes = {}

            for row in rows:
                team_id = row['team_id']
                prize_type = row['prize_type']

                if team_id not in prizes:
                    prizes[team_id] = {}

                prizes[team_id][prize_type] = {
                    'name': row['prize_name'],
                    'description': row['prize_description'],
                    'awarded_at': row['awarded_at'],
                    'effects': json.loads(row['effects'])
                }

            return prizes
        except Exception as e:
            logger.error(f"Error loading prizes: {str(e)}")
            return {}

    def load_game_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a game state from the database.

        Args:
            game_id: The ID of the game to load.

        Returns:
            The game state, or None if not found.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get game data
            cursor.execute('SELECT * FROM games WHERE game_id = ?', (game_id,))
            game_row = cursor.fetchone()

            if not game_row:
                return None

            # Get teams
            cursor.execute('SELECT * FROM teams WHERE game_id = ?', (game_id,))
            team_rows = cursor.fetchall()

            # Get prizes
            prizes = self.load_prizes(game_id)

            # Build game state
            game_state = {
                'game_id': game_row['game_id'],
                'created_at': game_row['created_at'],
                'current_round': game_row['current_round'],
                'current_year': game_row['current_year'],
                'game_started': bool(game_row['game_started']),
                'game_ended': bool(game_row['game_ended']),
                'teams': {},
                'prizes': prizes
            }

            # Add teams
            for team_row in team_rows:
                team_id = team_row['team_id']
                game_state['teams'][team_id] = {
                    'team_id': team_id,
                    'team_name': team_row['team_name'],
                    'created_at': team_row['created_at'],
                    'eliminated': bool(team_row['eliminated'])
                }

            return game_state
        except Exception as e:
            logger.error(f"Error loading game state: {str(e)}")
            return None

    def delete_game(self, game_id: str) -> bool:
        """
        Delete a game and all associated data from the database.

        Args:
            game_id: The ID of the game to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Delete prizes first (due to foreign key constraints)
            cursor.execute('DELETE FROM prizes WHERE game_id = ?', (game_id,))

            # Delete teams
            cursor.execute('DELETE FROM teams WHERE game_id = ?', (game_id,))

            # Delete game
            cursor.execute('DELETE FROM games WHERE game_id = ?', (game_id,))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting game: {str(e)}")
            conn.rollback()
            return False

    def close(self):
        """Close the database connection."""
        if hasattr(_local, 'connection'):
            _local.connection.close()
            del _local.connection
