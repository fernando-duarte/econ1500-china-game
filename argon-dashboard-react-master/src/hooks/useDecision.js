import { useContext } from 'react';
import { DecisionContext } from '../providers/DecisionProvider';

/**
 * useDecision hook to access decision submission context.
 */
export const useDecision = () => useContext(DecisionContext); 