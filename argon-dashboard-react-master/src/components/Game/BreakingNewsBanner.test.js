import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BreakingNewsBanner from './BreakingNewsBanner';

describe('BreakingNewsBanner', () => {
  it('renders the banner with the correct message', () => {
    render(<BreakingNewsBanner message="China joins the WTO!" onDismiss={() => {}} />);
    expect(screen.getByText('BREAKING NEWS:')).toBeInTheDocument();
    expect(screen.getByText('China joins the WTO!')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('calls onDismiss when the close button is clicked', () => {
    const onDismiss = jest.fn();
    render(<BreakingNewsBanner message="Event!" onDismiss={onDismiss} />);
    const closeBtn = screen.getByLabelText('Close breaking news banner');
    fireEvent.click(closeBtn);
    expect(onDismiss).toHaveBeenCalled();
  });

  it('is accessible with aria-live and role', () => {
    render(<BreakingNewsBanner message="Event!" onDismiss={() => {}} />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'polite');
    expect(alert).toHaveAttribute('aria-atomic', 'true');
  });
}); 