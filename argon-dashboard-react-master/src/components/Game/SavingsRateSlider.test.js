import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SavingsRateSlider from './SavingsRateSlider';

/**
 * Unit tests for SavingsRateSlider
 */
describe('SavingsRateSlider', () => {
  it('renders with correct label and value', () => {
    render(<SavingsRateSlider value={50} onChange={() => {}} />);
    expect(screen.getByText('Savings Rate (% of GDP)')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toHaveAttribute('aria-valuenow', '50');
  });

  it('does not allow selecting 0 or 100', () => {
    const handleChange = jest.fn();
    render(<SavingsRateSlider value={50} onChange={handleChange} />);
    const slider = screen.getByRole('slider');
    // Try to set to 0
    fireEvent.change(slider, { target: { value: 0 } });
    expect(handleChange).toHaveBeenCalledWith(1);
    // Try to set to 100
    fireEvent.change(slider, { target: { value: 100 } });
    expect(handleChange).toHaveBeenCalledWith(99);
  });

  it('allows selecting values between 1 and 99', () => {
    const handleChange = jest.fn();
    render(<SavingsRateSlider value={50} onChange={handleChange} />);
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: 25 } });
    expect(handleChange).toHaveBeenCalledWith(25);
    fireEvent.change(slider, { target: { value: 99 } });
    expect(handleChange).toHaveBeenCalledWith(99);
    fireEvent.change(slider, { target: { value: 1 } });
    expect(handleChange).toHaveBeenCalledWith(1);
  });

  it('is accessible with aria labels', () => {
    render(<SavingsRateSlider value={50} onChange={() => {}} />);
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('aria-labelledby', 'savings-rate-slider-label');
  });
}); 