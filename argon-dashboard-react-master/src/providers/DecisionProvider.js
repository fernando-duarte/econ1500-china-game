import React, { createContext, useContext, useState, useEffect } from 'react';
import { emit, on, off } from '../api/socket';

/**
 * DecisionContext provides submitDecision, submitting, error, confirmation, and reset.
 */
export const DecisionContext = createContext();

/**
 * DecisionProvider wraps children and provides decision submission context.
 * Submits decisions via WebSocket and listens for confirmation/error.
 */
export const DecisionProvider = ({ children }) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [confirmation, setConfirmation] = useState(null);

  useEffect(() => {
    // Listen for decision result from server
    const handleDecisionResult = (data) => {
      setSubmitting(false);
      if (data.success) {
        setConfirmation({ success: true, message: data.message || 'Decision submitted!' });
        setError(null);
      } else {
        setError(data.message || 'Submission failed');
        setConfirmation(null);
      }
    };
    on('decisionResult', handleDecisionResult);
    return () => {
      off('decisionResult', handleDecisionResult);
    };
    // eslint-disable-next-line
  }, []);

  const submitDecision = async (decision) => {
    setSubmitting(true);
    setError(null);
    setConfirmation(null);
    emit('submitDecision', decision);
  };

  const reset = () => {
    setError(null);
    setConfirmation(null);
  };

  return (
    <DecisionContext.Provider value={{ submitDecision, submitting, error, confirmation, reset }}>
      {children}
    </DecisionContext.Provider>
  );
}; 