import React, { createContext, useContext, useState, useEffect } from 'react';
import { getGameState, getTeamStats } from '../api/gameStateApi';
import { on, off } from '../api/socket';

/**
 * GameStateContext provides game state, team stats, loading, error, and refresh.
 */
export const GameStateContext = createContext();

/**
 * GameStateProvider wraps children and provides game state context.
 * Fetches initial data from API and subscribes to WebSocket updates.
 */
export const GameStateProvider = ({ children }) => {
  const [gameState, setGameState] = useState(null);
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Replace with actual team ID logic as needed
  const teamId = 'demo-team';

  // Fetch initial data from API
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [gs, ts] = await Promise.all([
        getGameState(),
        getTeamStats(teamId),
      ]);
      setGameState(gs);
      setTeamStats(ts);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // Subscribe to WebSocket events for real-time updates
  useEffect(() => {
    fetchData();
    // Example event names: 'gameStateUpdate', 'teamStatsUpdate'
    const handleGameStateUpdate = (data) => setGameState(data);
    const handleTeamStatsUpdate = (data) => setTeamStats(data);
    on('gameStateUpdate', handleGameStateUpdate);
    on('teamStatsUpdate', handleTeamStatsUpdate);
    return () => {
      off('gameStateUpdate', handleGameStateUpdate);
      off('teamStatsUpdate', handleTeamStatsUpdate);
    };
    // eslint-disable-next-line
  }, []);

  const refresh = fetchData;

  return (
    <GameStateContext.Provider value={{ gameState, teamStats, loading, error, refresh }}>
      {children}
    </GameStateContext.Provider>
  );
}; 