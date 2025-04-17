import { useContext } from 'react';
import { GameStateContext } from '../providers/GameStateProvider';

/**
 * useGameState hook to access game state context.
 */
export const useGameState = () => useContext(GameStateContext); 