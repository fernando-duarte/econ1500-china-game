import React from 'react';
import PropTypes from 'prop-types';
import { Line } from 'react-chartjs-2';
import { chartOptions } from 'variables/charts.js';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

/**
 * GDPGrowthChart component
 * Displays a line chart of GDP growth over time.
 * Uses Argon Dashboard's default chart style.
 *
 * @param {number[]} data - Array of GDP growth values (percent)
 * @param {string[]} labels - Array of labels (years/rounds)
 */
const GDPGrowthChart = ({ data, labels }) => {
  const chartData = {
    labels,
    datasets: [
      {
        label: 'GDP Growth (%)',
        data,
        fill: false,
        backgroundColor: '#5e72e4', // Argon primary
        borderColor: '#5e72e4',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Typography variant="h6" component="div" gutterBottom>
        GDP Growth Over Time
      </Typography>
      <Line
        data={chartData}
        options={{ ...chartOptions(), responsive: true, plugins: { legend: { display: false } } }}
        aria-label="GDP Growth Chart"
        role="img"
      />
    </Box>
  );
};

GDPGrowthChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.number).isRequired,
  labels: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default GDPGrowthChart; 