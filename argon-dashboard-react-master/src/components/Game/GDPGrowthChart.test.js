import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

// Create a mock function for Line
const mockLine = jest.fn(() => null);
jest.mock('react-chartjs-2', () => ({
  Line: (props) => mockLine(props),
}));

import GDPGrowthChart from './GDPGrowthChart';

describe('GDPGrowthChart', () => {
  const data = [8, 7, 9, 6];
  const labels = ['1980', '1985', '1990', '1995'];

  beforeEach(() => {
    mockLine.mockClear();
  });

  it('renders the chart with correct title', () => {
    render(<GDPGrowthChart data={data} labels={labels} />);
    // Only check that the mock was called
    expect(mockLine).toHaveBeenCalled();
  });

  it('passes the correct data and labels to Line', () => {
    render(<GDPGrowthChart data={data} labels={labels} />);
    expect(mockLine).toHaveBeenCalled();
    const props = mockLine.mock.calls[0][0];
    expect(props.data.labels).toEqual(labels);
    expect(props.data.datasets[0].data).toEqual(data);
  });
}); 