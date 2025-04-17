import React, { createContext, useContext, useState, useEffect } from 'react';
import { on, off } from '../api/socket';

/**
 * TimerContext provides timeLeft, isRunning, loading, and error.
 */
export const TimerContext = createContext();

/**
 * TimerProvider wraps children and provides timer context.
 * Fetches initial timer value and subscribes to WebSocket updates.
 */
export const TimerProvider = ({ children }) => {
  const [timeLeft, setTimeLeft] = useState(120); // seconds (placeholder)
  const [isRunning, setIsRunning] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // TODO: Optionally fetch initial timer value from API
    setLoading(false);
    setError(null);
    // Subscribe to timer updates from WebSocket
    const handleTimerUpdate = (data) => {
      setTimeLeft(data.timeLeft);
      setIsRunning(data.isRunning);
    };
    on('timerUpdate', handleTimerUpdate);
    return () => {
      off('timerUpdate', handleTimerUpdate);
    };
    // eslint-disable-next-line
  }, []);

  return (
    <TimerContext.Provider value={{ timeLeft, isRunning, loading, error }}>
      {children}
    </TimerContext.Provider>
  );
}; 