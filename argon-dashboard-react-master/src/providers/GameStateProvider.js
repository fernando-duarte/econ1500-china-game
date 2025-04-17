import React, { createContext, useContext, useState } from 'react';

/**
 * GameStateContext provides game state, team stats, loading, error, and refresh.
 */
export const GameStateContext = createContext();

/**
 * GameStateProvider wraps children and provides game state context.
 * Placeholder implementation for now.
 */
export const GameStateProvider = ({ children }) => {
  const [gameState, setGameState] = useState(null); // TODO: fetch from API
  const [teamStats, setTeamStats] = useState(null); // TODO: fetch from API
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refresh = () => {
    // TODO: implement API refresh
  };

  return (
    <GameStateContext.Provider value={{ gameState, teamStats, loading, error, refresh }}>
      {children}
    </GameStateContext.Provider>
  );
}; 