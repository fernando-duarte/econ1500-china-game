import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExchangeRateButtons from './ExchangeRateButtons';

describe('ExchangeRateButtons', () => {
  const options = ['Undervalue', 'Market-based', 'Overvalued'];

  it('renders all options and highlights the selected one', () => {
    render(
      <ExchangeRateButtons selected="Market-based" onSelect={() => {}} options={options} />
    );
    options.forEach((option) => {
      expect(screen.getByRole('button', { name: option })).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Market-based' })).toHaveClass('active');
    expect(screen.getByRole('button', { name: 'Undervalue' })).not.toHaveClass('active');
    expect(screen.getByRole('button', { name: 'Overvalued' })).not.toHaveClass('active');
  });

  it('calls onSelect with the correct value when clicked', () => {
    const handleSelect = jest.fn();
    render(
      <ExchangeRateButtons selected="Undervalue" onSelect={handleSelect} options={options} />
    );
    fireEvent.click(screen.getByRole('button', { name: 'Overvalued' }));
    expect(handleSelect).toHaveBeenCalledWith('Overvalued');
  });

  it('is accessible with aria attributes', () => {
    render(
      <ExchangeRateButtons selected="Undervalue" onSelect={() => {}} options={options} />
    );
    options.forEach((option) => {
      const btn = screen.getByRole('button', { name: option });
      expect(btn).toHaveAttribute('aria-label', option);
      expect(btn).toHaveAttribute('aria-pressed');
    });
    expect(screen.getByRole('group')).toHaveAttribute('aria-label', 'Exchange Rate Selection');
  });
}); 