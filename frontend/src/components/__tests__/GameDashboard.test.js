import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import GameDashboard from '../GameDashboard';
import { GameContext } from '../../contexts/GameContext';
import { SocketContext } from '../../contexts/SocketContext';

// Mock the socket context
const mockSocket = {
  emit: jest.fn(),
  on: jest.fn(),
  off: jest.fn()
};

// Mock the game context
const mockGameState = {
  gameId: 'test-game-id',
  currentRound: 1,
  currentYear: 1985,
  teams: {
    'team1': {
      teamId: 'team1',
      teamName: 'Test Team',
      currentState: {
        GDP: 1000,
        'Net Exports': 50,
        Consumption: 800,
        Investment: 200
      }
    }
  },
  rankings: {
    gdp: ['team1'],
    netExports: ['team1'],
    balancedEconomy: ['team1']
  },
  gameStarted: true,
  gameEnded: false
};

const mockGameContext = {
  gameState: mockGameState,
  setGameState: jest.fn(),
  currentTeam: {
    teamId: 'team1',
    teamName: 'Test Team'
  },
  setCurrentTeam: jest.fn(),
  isAdmin: false
};

describe('GameDashboard', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });
  
  it('renders the dashboard with game information', () => {
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={mockGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Check that basic game info is displayed
    expect(screen.getByText(/Round 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Year 1985/i)).toBeInTheDocument();
    expect(screen.getByText(/Test Team/i)).toBeInTheDocument();
    
    // Check that economic indicators are displayed
    expect(screen.getByText(/GDP/i)).toBeInTheDocument();
    expect(screen.getByText(/1000/i)).toBeInTheDocument();
    expect(screen.getByText(/Net Exports/i)).toBeInTheDocument();
    expect(screen.getByText(/50/i)).toBeInTheDocument();
  });
  
  it('allows submitting decisions when game is started', async () => {
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={mockGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Find the savings rate input and exchange rate select
    const savingsRateInput = screen.getByLabelText(/Savings Rate/i);
    const exchangeRateSelect = screen.getByLabelText(/Exchange Rate Policy/i);
    
    // Change the values
    fireEvent.change(savingsRateInput, { target: { value: '0.3' } });
    fireEvent.change(exchangeRateSelect, { target: { value: 'undervalue' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit Decision/i });
    fireEvent.click(submitButton);
    
    // Check that the socket emit was called with the correct values
    await waitFor(() => {
      expect(mockSocket.emit).toHaveBeenCalledWith('submitDecision', {
        teamId: 'team1',
        savingsRate: 0.3,
        exchangeRatePolicy: 'undervalue'
      });
    });
  });
  
  it('disables decision submission when game is not started', () => {
    // Create a game state where the game is not started
    const notStartedGameContext = {
      ...mockGameContext,
      gameState: {
        ...mockGameState,
        gameStarted: false
      }
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={notStartedGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Check that the submit button is disabled
    const submitButton = screen.getByRole('button', { name: /Submit Decision/i });
    expect(submitButton).toBeDisabled();
  });
  
  it('shows admin controls for admin users', () => {
    // Create a game context where the user is an admin
    const adminGameContext = {
      ...mockGameContext,
      isAdmin: true
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={adminGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Check that admin controls are displayed
    expect(screen.getByRole('button', { name: /Start Game/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Next Round/i })).toBeInTheDocument();
  });
  
  it('allows admin to start the game', async () => {
    // Create a game context where the user is an admin
    const adminGameContext = {
      ...mockGameContext,
      isAdmin: true,
      gameState: {
        ...mockGameState,
        gameStarted: false
      }
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={adminGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Click the start game button
    const startButton = screen.getByRole('button', { name: /Start Game/i });
    fireEvent.click(startButton);
    
    // Check that the socket emit was called
    await waitFor(() => {
      expect(mockSocket.emit).toHaveBeenCalledWith('startGame');
    });
  });
  
  it('allows admin to advance to the next round', async () => {
    // Create a game context where the user is an admin
    const adminGameContext = {
      ...mockGameContext,
      isAdmin: true
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={adminGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Click the next round button
    const nextRoundButton = screen.getByRole('button', { name: /Next Round/i });
    fireEvent.click(nextRoundButton);
    
    // Check that the socket emit was called
    await waitFor(() => {
      expect(mockSocket.emit).toHaveBeenCalledWith('nextRound');
    });
  });
  
  it('subscribes to socket events on mount and unsubscribes on unmount', () => {
    const { unmount } = render(
      <SocketContext.Provider value={mockSocket}>
        <GameContext.Provider value={mockGameContext}>
          <GameDashboard />
        </GameContext.Provider>
      </SocketContext.Provider>
    );
    
    // Check that socket.on was called for the expected events
    expect(mockSocket.on).toHaveBeenCalledWith('gameState', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('decisionSubmitted', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('gameStarted', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('roundAdvanced', expect.any(Function));
    
    // Unmount the component
    unmount();
    
    // Check that socket.off was called for the expected events
    expect(mockSocket.off).toHaveBeenCalledWith('gameState', expect.any(Function));
    expect(mockSocket.off).toHaveBeenCalledWith('decisionSubmitted', expect.any(Function));
    expect(mockSocket.off).toHaveBeenCalledWith('gameStarted', expect.any(Function));
    expect(mockSocket.off).toHaveBeenCalledWith('roundAdvanced', expect.any(Function));
  });
});
