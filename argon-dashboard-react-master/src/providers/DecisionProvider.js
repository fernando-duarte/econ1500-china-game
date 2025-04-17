import React, { createContext, useContext, useState } from 'react';

/**
 * DecisionContext provides submitDecision, submitting, error, confirmation, and reset.
 */
export const DecisionContext = createContext();

/**
 * DecisionProvider wraps children and provides decision submission context.
 * Placeholder implementation for now.
 */
export const DecisionProvider = ({ children }) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [confirmation, setConfirmation] = useState(null);

  const submitDecision = async (decision) => {
    setSubmitting(true);
    setError(null);
    // TODO: implement API/WebSocket submission
    setTimeout(() => {
      setConfirmation({ success: true, message: 'Decision submitted!' });
      setSubmitting(false);
    }, 1000);
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