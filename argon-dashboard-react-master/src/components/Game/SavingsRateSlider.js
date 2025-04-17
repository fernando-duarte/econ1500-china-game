import React from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';

/**
 * SavingsRateSlider component
 * Displays a slider from 0 to 100, but only allows values 1-99.
 * If user selects 0 or 100, snaps to 1 or 99.
 * Accessible and responsive.
 *
 * @param {number} value - Current savings rate (1-99)
 * @param {function} onChange - Callback when value changes
 */
const SavingsRateSlider = ({ value, onChange }) => {
  // Handler to enforce 1-99 range
  const handleChange = (event, newValue) => {
    let safeValue = newValue;
    if (newValue <= 0) safeValue = 1;
    if (newValue >= 100) safeValue = 99;
    onChange(safeValue);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 400, mx: 'auto', p: 2 }}>
      <Typography id="savings-rate-slider-label" gutterBottom>
        Savings Rate (% of GDP)
      </Typography>
      <Slider
        aria-labelledby="savings-rate-slider-label"
        value={value}
        min={0}
        max={100}
        step={1}
        marks={[{ value: 0, label: '0%' }, { value: 100, label: '100%' }]}
        valueLabelDisplay="auto"
        onChange={handleChange}
        sx={{ mt: 3 }}
      />
    </Box>
  );
};

SavingsRateSlider.propTypes = {
  value: PropTypes.number.isRequired, // Must be 1-99
  onChange: PropTypes.func.isRequired,
};

export default SavingsRateSlider; 