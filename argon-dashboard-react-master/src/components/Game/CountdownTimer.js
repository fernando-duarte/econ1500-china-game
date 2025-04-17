import React, { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

/**
 * CountdownTimer component
 * Displays time remaining in M:SS format (one digit for minutes, two for seconds).
 * Calls onComplete when timer reaches zero.
 * Accessible and responsive.
 *
 * @param {Date|number} endTime - The end time as a Date object or timestamp (ms)
 * @param {function} onComplete - Callback when timer reaches zero
 */
const CountdownTimer = ({ endTime, onComplete }) => {
  const [remaining, setRemaining] = useState(() => Math.max(0, Math.floor((new Date(endTime) - Date.now()) / 1000)));
  const intervalRef = useRef();

  useEffect(() => {
    function update() {
      const seconds = Math.max(0, Math.floor((new Date(endTime) - Date.now()) / 1000));
      setRemaining(seconds);
      if (seconds === 0 && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        if (onComplete) onComplete();
      }
    }
    intervalRef.current = setInterval(update, 1000);
    update();
    return () => clearInterval(intervalRef.current);
  }, [endTime, onComplete]);

  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const formatted = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <Box sx={{ width: '100%', textAlign: 'center', p: 2 }}>
      <Typography
        variant="h4"
        component="div"
        aria-live="polite"
        aria-atomic="true"
        sx={{ fontWeight: 'bold', letterSpacing: 2 }}
      >
        {formatted}
      </Typography>
    </Box>
  );
};

CountdownTimer.propTypes = {
  endTime: PropTypes.oneOfType([
    PropTypes.instanceOf(Date),
    PropTypes.number,
    PropTypes.string,
  ]).isRequired,
  onComplete: PropTypes.func,
};

export default CountdownTimer; 