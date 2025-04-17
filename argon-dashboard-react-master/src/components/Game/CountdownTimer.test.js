import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import CountdownTimer from './CountdownTimer';

jest.useFakeTimers();

describe('CountdownTimer', () => {
  it('displays time in M:SS format', () => {
    const now = Date.now();
    render(<CountdownTimer endTime={now + 65000} />); // 1:05
    expect(screen.getByText('1:05')).toBeInTheDocument();
  });

  it('counts down and calls onComplete at zero', () => {
    const now = Date.now();
    const onComplete = jest.fn();
    render(<CountdownTimer endTime={now + 2000} onComplete={onComplete} />);
    expect(screen.getByText('0:02')).toBeInTheDocument();
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(screen.getByText('0:01')).toBeInTheDocument();
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(screen.getByText('0:00')).toBeInTheDocument();
    expect(onComplete).toHaveBeenCalled();
  });

  it('is accessible with aria-live', () => {
    const now = Date.now();
    render(<CountdownTimer endTime={now + 10000} />);
    const timer = screen.getByText(/:/);
    expect(timer).toHaveAttribute('aria-live', 'polite');
    expect(timer).toHaveAttribute('aria-atomic', 'true');
  });
}); 