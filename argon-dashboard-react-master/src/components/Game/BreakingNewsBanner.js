import React from 'react';
import PropTypes from 'prop-types';
import { Alert } from 'reactstrap';

/**
 * BreakingNewsBanner component
 * Dismissible info alert/banner for breaking news events.
 * Styled with Argon Dashboard's info alert style.
 *
 * @param {string} message - The breaking news message
 * @param {function} onDismiss - Callback when banner is dismissed
 */
const BreakingNewsBanner = ({ message, onDismiss }) => {
  return (
    <Alert
      color="info"
      isOpen={!!message}
      toggle={onDismiss}
      className="mb-4"
      aria-live="polite"
      aria-atomic="true"
      role="alert"
      fade
    >
      <span className="font-weight-bold mr-2">BREAKING NEWS:</span>
      {message}
      <button
        type="button"
        className="close"
        aria-label="Close breaking news banner"
        onClick={onDismiss}
        style={{ position: 'absolute', right: 16, top: 16 }}
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </Alert>
  );
};

BreakingNewsBanner.propTypes = {
  message: PropTypes.string.isRequired,
  onDismiss: PropTypes.func.isRequired,
};

export default BreakingNewsBanner; 