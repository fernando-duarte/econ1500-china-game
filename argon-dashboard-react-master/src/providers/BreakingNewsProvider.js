import React, { createContext, useContext, useState, useEffect } from 'react';
import { on, off } from '../api/socket';

/**
 * BreakingNewsContext provides news, loading, error, and dismiss.
 */
export const BreakingNewsContext = createContext();

/**
 * BreakingNewsProvider wraps children and provides breaking news context.
 * Subscribes to WebSocket breaking news events.
 */
export const BreakingNewsProvider = ({ children }) => {
  const [news, setNews] = useState(null); // No news by default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // TODO: Optionally fetch initial news from API
    setLoading(false);
    setError(null);
    // Subscribe to breaking news events from WebSocket
    const handleBreakingNews = (data) => setNews(data);
    on('breakingNews', handleBreakingNews);
    return () => {
      off('breakingNews', handleBreakingNews);
    };
    // eslint-disable-next-line
  }, []);

  const dismiss = () => setNews(null);

  return (
    <BreakingNewsContext.Provider value={{ news, loading, error, dismiss }}>
      {children}
    </BreakingNewsContext.Provider>
  );
}; 