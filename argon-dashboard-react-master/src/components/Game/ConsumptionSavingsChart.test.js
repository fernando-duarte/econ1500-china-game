import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

// Create a mock function for Pie
const mockPie = jest.fn(() => null);
jest.mock('react-chartjs-2', () => ({
  Pie: (props) => mockPie(props),
}));

import ConsumptionSavingsChart from './ConsumptionSavingsChart';

describe('ConsumptionSavingsChart', () => {
  beforeEach(() => {
    mockPie.mockClear();
  });

  it('renders the chart', () => {
    render(<ConsumptionSavingsChart consumption={1200} savings={800} />);
    // Only check that the mock was called
    expect(mockPie).toHaveBeenCalled();
  });

  it('passes the correct data to Pie', () => {
    render(<ConsumptionSavingsChart consumption={1200} savings={800} />);
    expect(mockPie).toHaveBeenCalled();
    const props = mockPie.mock.calls[0][0];
    expect(props.data.datasets[0].data).toEqual([1200, 800]);
  });
}); 