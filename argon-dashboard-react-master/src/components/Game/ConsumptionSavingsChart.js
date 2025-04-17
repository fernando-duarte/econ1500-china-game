import React from 'react';
import PropTypes from 'prop-types';
import { Pie } from 'react-chartjs-2';
import { chartOptions } from 'variables/charts.js';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

/**
 * ConsumptionSavingsChart component
 * Displays a pie chart of consumption vs. savings.
 * Uses Argon Dashboard's default pie chart colors.
 *
 * @param {number} consumption - Consumption value
 * @param {number} savings - Savings value
 */
const ConsumptionSavingsChart = ({ consumption, savings }) => {
  const chartData = {
    labels: ['Consumption', 'Savings'],
    datasets: [
      {
        data: [consumption, savings],
        backgroundColor: ['#5e72e4', '#2dce89'], // Argon default: primary, success
        borderColor: ['#fff', '#fff'],
        borderWidth: 2,
      },
    ],
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Typography variant="h6" component="div" gutterBottom>
        Consumption vs. Savings
      </Typography>
      <Pie
        data={chartData}
        options={{ ...chartOptions(), responsive: true, plugins: { legend: { display: true } } }}
        aria-label="Consumption vs Savings Chart"
        role="img"
      />
    </Box>
  );
};

ConsumptionSavingsChart.propTypes = {
  consumption: PropTypes.number.isRequired,
  savings: PropTypes.number.isRequired,
};

export default ConsumptionSavingsChart; 