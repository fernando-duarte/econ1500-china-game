import React from 'react';
import PropTypes from 'prop-types';
import { Bar } from 'react-chartjs-2';
import { chartOptions, chartExample2 } from 'variables/charts.js';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

/**
 * TradeBalanceChart component
 * Displays a bar chart of trade balance over time.
 * Uses Argon Dashboard's default bar style.
 *
 * @param {number[]} data - Array of trade balance values
 * @param {string[]} labels - Array of labels (years/rounds)
 */
const TradeBalanceChart = ({ data, labels }) => {
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Trade Balance',
        data,
        backgroundColor: chartExample2.data.datasets[0].backgroundColor || '#11cdef', // Argon default
        borderColor: chartExample2.data.datasets[0].borderColor || '#11cdef',
        borderWidth: 2,
        barPercentage: 0.6,
        categoryPercentage: 0.5,
      },
    ],
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Typography variant="h6" component="div" gutterBottom>
        Trade Balance Over Time
      </Typography>
      <Bar
        data={chartData}
        options={{ ...chartOptions(), responsive: true, plugins: { legend: { display: false } } }}
        aria-label="Trade Balance Chart"
        role="img"
      />
    </Box>
  );
};

TradeBalanceChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.number).isRequired,
  labels: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default TradeBalanceChart; 