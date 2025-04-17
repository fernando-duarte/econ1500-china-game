import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import EconomicStats from './EconomicStats';

describe('EconomicStats', () => {
  const baseStats = {
    groupName: 'The Prosperous Pandas',
    year: 2005,
    gdp: 2500,
    gdpGrowth: 8,
    consumption: 1200,
    netExports: 200,
    capitalStock: 1800,
    ranking: { current: 2, total: 10 },
    isHot: true,
  };

  it('renders all stats in the correct order and format', () => {
    render(<EconomicStats stats={baseStats} />);
    expect(screen.getByText('The Prosperous Pandas')).toBeInTheDocument();
    expect(screen.getByText('Year: 2005')).toBeInTheDocument();
    expect(screen.getByText('GDP:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('$2,500 bn')).toBeInTheDocument();
    expect(screen.getByText('GDP Growth:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('+8%')).toBeInTheDocument();
    expect(screen.getByText('Consumption:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('$1,200 bn')).toBeInTheDocument();
    expect(screen.getByText('Net Exports:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('+$200 bn')).toBeInTheDocument();
    expect(screen.getByText('Capital Stock:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('$1,800 bn')).toBeInTheDocument();
    expect(screen.getByText('Ranking:', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('#2 of 10 groups 🔥')).toBeInTheDocument();
  });

  it('formats negative net exports and zero growth correctly', () => {
    const stats = { ...baseStats, netExports: -50, gdpGrowth: 0, isHot: false };
    render(<EconomicStats stats={stats} />);
    expect(screen.getByText('$-50 bn')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('#2 of 10 groups')).toBeInTheDocument();
  });

  it('is accessible with aria-labels', () => {
    render(<EconomicStats stats={baseStats} />);
    expect(screen.getByLabelText('Group Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Current Year')).toBeInTheDocument();
    expect(screen.getByLabelText('GDP')).toBeInTheDocument();
    expect(screen.getByLabelText('GDP Growth')).toBeInTheDocument();
    expect(screen.getByLabelText('Consumption')).toBeInTheDocument();
    expect(screen.getByLabelText('Net Exports')).toBeInTheDocument();
    expect(screen.getByLabelText('Capital Stock')).toBeInTheDocument();
    expect(screen.getByLabelText('Ranking')).toBeInTheDocument();
  });
}); 