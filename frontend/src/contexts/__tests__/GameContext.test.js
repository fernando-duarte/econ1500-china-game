import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { GameProvider, useGameContext } from '../GameContext';
import { SocketContext } from '../SocketContext';

// Mock the socket context
const mockSocket = {
  emit: jest.fn(),
  on: jest.fn(),
  off: jest.fn()
};

// Create a test component that uses the game context
const TestComponent = () => {
  const { gameState, currentTeam, isAdmin } = useGameContext();
  
  return (
    <div>
      <div data-testid="game-id">{gameState.gameId}</div>
      <div data-testid="current-round">{gameState.currentRound}</div>
      <div data-testid="team-id">{currentTeam?.teamId}</div>
      <div data-testid="is-admin">{isAdmin ? 'Yes' : 'No'}</div>
    </div>
  );
};

describe('GameContext', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn();
    Storage.prototype.setItem = jest.fn();
  });
  
  it('provides default game state', () => {
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <TestComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Check that default values are provided
    expect(screen.getByTestId('game-id')).toHaveTextContent('');
    expect(screen.getByTestId('current-round')).toHaveTextContent('0');
    expect(screen.getByTestId('team-id')).toHaveTextContent('');
    expect(screen.getByTestId('is-admin')).toHaveTextContent('No');
  });
  
  it('loads team data from localStorage', () => {
    // Mock localStorage to return team data
    Storage.prototype.getItem.mockImplementation((key) => {
      if (key === 'teamId') return 'team1';
      if (key === 'teamName') return 'Test Team';
      if (key === 'isAdmin') return 'true';
      return null;
    });
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <TestComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Check that team data was loaded from localStorage
    expect(screen.getByTestId('team-id')).toHaveTextContent('team1');
    expect(screen.getByTestId('is-admin')).toHaveTextContent('Yes');
  });
  
  it('subscribes to socket events on mount', () => {
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <TestComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Check that socket.on was called for the expected events
    expect(mockSocket.on).toHaveBeenCalledWith('gameState', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('gameStarted', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('roundAdvanced', expect.any(Function));
  });
  
  it('updates game state when receiving socket events', () => {
    // Capture the event handlers
    const eventHandlers = {};
    mockSocket.on.mockImplementation((event, handler) => {
      eventHandlers[event] = handler;
    });
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <TestComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Simulate receiving a gameState event
    act(() => {
      eventHandlers.gameState({
        gameId: 'test-game-id',
        currentRound: 1,
        currentYear: 1985,
        teams: {
          'team1': {
            teamId: 'team1',
            teamName: 'Test Team'
          }
        },
        rankings: {},
        gameStarted: true,
        gameEnded: false
      });
    });
    
    // Check that the game state was updated
    expect(screen.getByTestId('game-id')).toHaveTextContent('test-game-id');
    expect(screen.getByTestId('current-round')).toHaveTextContent('1');
  });
  
  it('saves team data to localStorage when it changes', () => {
    // Create a wrapper component that can update the current team
    const WrapperComponent = () => {
      const { setCurrentTeam } = useGameContext();
      
      React.useEffect(() => {
        // Update the current team
        setCurrentTeam({
          teamId: 'team2',
          teamName: 'New Team'
        });
      }, [setCurrentTeam]);
      
      return <TestComponent />;
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <WrapperComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Check that localStorage.setItem was called with the new team data
    expect(Storage.prototype.setItem).toHaveBeenCalledWith('teamId', 'team2');
    expect(Storage.prototype.setItem).toHaveBeenCalledWith('teamName', 'New Team');
  });
  
  it('provides methods to update game state', () => {
    // Create a wrapper component that can update the game state
    const WrapperComponent = () => {
      const { setGameState } = useGameContext();
      
      React.useEffect(() => {
        // Update the game state
        setGameState({
          gameId: 'new-game-id',
          currentRound: 2,
          currentYear: 1990,
          teams: {},
          rankings: {},
          gameStarted: true,
          gameEnded: false
        });
      }, [setGameState]);
      
      return <TestComponent />;
    };
    
    render(
      <SocketContext.Provider value={mockSocket}>
        <GameProvider>
          <WrapperComponent />
        </GameProvider>
      </SocketContext.Provider>
    );
    
    // Check that the game state was updated
    expect(screen.getByTestId('game-id')).toHaveTextContent('new-game-id');
    expect(screen.getByTestId('current-round')).toHaveTextContent('2');
  });
});
