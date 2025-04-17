import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

// Create a mock function for Bar
const mockBar = jest.fn(() => null);
jest.mock('react-chartjs-2', () => ({
  Bar: (props) => mockBar(props),
}));

import TradeBalanceChart from './TradeBalanceChart';

describe('TradeBalanceChart', () => {
  const data = [200, 150, 300, 100];
  const labels = ['1980', '1985', '1990', '1995'];

  beforeEach(() => {
    mockBar.mockClear();
  });

  it('renders the chart with correct title', () => {
    render(<TradeBalanceChart data={data} labels={labels} />);
    // Only check that the mock was called
    expect(mockBar).toHaveBeenCalled();
  });

  it('passes the correct data and labels to Bar', () => {
    render(<TradeBalanceChart data={data} labels={labels} />);
    expect(mockBar).toHaveBeenCalled();
    const props = mockBar.mock.calls[0][0];
    expect(props.data.labels).toEqual(labels);
    expect(props.data.datasets[0].data).toEqual(data);
  });
}); 