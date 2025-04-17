import { useContext } from 'react';
import { TimerContext } from '../providers/TimerProvider';

/**
 * useTimer hook to access timer context.
 */
export const useTimer = () => useContext(TimerContext); 