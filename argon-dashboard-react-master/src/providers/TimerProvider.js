import React, { createContext, useContext, useState } from 'react';

/**
 * TimerContext provides timeLeft, isRunning, loading, and error.
 */
export const TimerContext = createContext();

/**
 * TimerProvider wraps children and provides timer context.
 * Placeholder implementation for now.
 */
export const TimerProvider = ({ children }) => {
  const [timeLeft, setTimeLeft] = useState(120); // seconds
  const [isRunning, setIsRunning] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // TODO: implement timer logic (API/WebSocket)

  return (
    <TimerContext.Provider value={{ timeLeft, isRunning, loading, error }}>
      {children}
    </TimerContext.Provider>
  );
}; 