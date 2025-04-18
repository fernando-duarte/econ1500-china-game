import axios from 'axios';
import ApiService from '../api-service';

// Mock axios
jest.mock('axios');

describe('ApiService', () => {
  let apiService;
  
  beforeEach(() => {
    // Create a new API service for each test
    apiService = new ApiService();
    
    // Reset axios mocks
    axios.get.mockReset();
    axios.post.mockReset();
  });
  
  describe('createTeam', () => {
    it('should call the API and return created team', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          team: {
            id: 'team1',
            name: 'Test Team',
            savingsRate: 0.3,
            exchangeRate: 'market',
            score: 0,
            history: []
          }
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      const result = await apiService.createTeam('Test Team');
      
      expect(axios.post).toHaveBeenCalledWith('/api/teams', { name: 'Test Team' });
      expect(result).toEqual(mockResponse.data.team);
    });
    
    it('should handle API errors', async () => {
      axios.post.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.createTeam('Test Team')).rejects.toThrow('API error');
    });
    
    it('should handle error responses', async () => {
      // Mock error response
      const mockResponse = {
        data: {
          success: false,
          message: 'Team name already taken'
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      await expect(apiService.createTeam('Test Team')).rejects.toThrow('Team name already taken');
    });
  });
  
  describe('getTeams', () => {
    it('should call the API and return teams', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          teams: {
            'team1': {
              id: 'team1',
              name: 'Test Team',
              savingsRate: 0.3,
              exchangeRate: 'market',
              score: 0,
              history: []
            }
          }
        }
      };
      
      axios.get.mockResolvedValue(mockResponse);
      
      const result = await apiService.getTeams();
      
      expect(axios.get).toHaveBeenCalledWith('/api/teams');
      expect(result).toEqual(mockResponse.data.teams);
    });
    
    it('should handle API errors', async () => {
      axios.get.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.getTeams()).rejects.toThrow('API error');
    });
    
    it('should handle error responses', async () => {
      // Mock error response
      const mockResponse = {
        data: {
          success: false,
          message: 'Failed to get teams'
        }
      };
      
      axios.get.mockResolvedValue(mockResponse);
      
      await expect(apiService.getTeams()).rejects.toThrow('Failed to get teams');
    });
  });
  
  describe('getTeam', () => {
    it('should call the API and return team', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          id: 'team1',
          name: 'Test Team',
          savingsRate: 0.3,
          exchangeRate: 'market',
          score: 0,
          history: []
        }
      };
      
      axios.get.mockResolvedValue(mockResponse);
      
      const result = await apiService.getTeam('team1');
      
      expect(axios.get).toHaveBeenCalledWith('/api/teams/team1');
      expect(result).toEqual(mockResponse.data);
    });
    
    it('should handle API errors', async () => {
      axios.get.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.getTeam('team1')).rejects.toThrow('API error');
    });
  });
  
  describe('submitDecision', () => {
    it('should call the API and return result', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          decision: {
            teamId: 'team1',
            round: 1,
            savingsRate: 0.3,
            exchangeRatePolicy: 'market',
            submittedAt: '2023-01-01T00:00:00'
          }
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      const result = await apiService.submitDecision('team1', 0.3, 'market');
      
      expect(axios.post).toHaveBeenCalledWith('/api/teams/team1/decisions', {
        savingsRate: 0.3,
        exchangeRatePolicy: 'market'
      });
      
      expect(result).toEqual(mockResponse.data.decision);
    });
    
    it('should handle API errors', async () => {
      axios.post.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.submitDecision('team1', 0.3, 'market')).rejects.toThrow('API error');
    });
    
    it('should handle error responses', async () => {
      // Mock error response
      const mockResponse = {
        data: {
          success: false,
          message: 'Invalid savings rate'
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      await expect(apiService.submitDecision('team1', 0.3, 'market')).rejects.toThrow('Invalid savings rate');
    });
  });
  
  describe('getGameState', () => {
    it('should call the API and return game state', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          gameState: {
            gameId: 'test-game-id',
            currentRound: 1,
            currentYear: 1985,
            teams: {
              'team1': {
                id: 'team1',
                name: 'Test Team'
              }
            },
            rankings: {},
            gameStarted: true,
            gameEnded: false
          }
        }
      };
      
      axios.get.mockResolvedValue(mockResponse);
      
      const result = await apiService.getGameState();
      
      expect(axios.get).toHaveBeenCalledWith('/api/game/state');
      expect(result).toEqual(mockResponse.data.gameState);
    });
    
    it('should handle API errors', async () => {
      axios.get.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.getGameState()).rejects.toThrow('API error');
    });
  });
  
  describe('startGame', () => {
    it('should call the API and return result', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          message: 'Game started'
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      const result = await apiService.startGame();
      
      expect(axios.post).toHaveBeenCalledWith('/api/game/start');
      expect(result).toEqual(mockResponse.data);
    });
    
    it('should handle API errors', async () => {
      axios.post.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.startGame()).rejects.toThrow('API error');
    });
  });
  
  describe('advanceRound', () => {
    it('should call the API and return result', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          success: true,
          message: 'Round advanced',
          round: 2,
          year: 1990
        }
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      const result = await apiService.advanceRound();
      
      expect(axios.post).toHaveBeenCalledWith('/api/game/next-round');
      expect(result).toEqual(mockResponse.data);
    });
    
    it('should handle API errors', async () => {
      axios.post.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.advanceRound()).rejects.toThrow('API error');
    });
  });
  
  describe('getTeamVisualizations', () => {
    it('should call the API and return visualization data', async () => {
      // Mock API response
      const mockResponse = {
        data: {
          gdp_growth_chart: {
            years: [1980, 1985, 1990],
            gdp_growth_percent: [0.0, 3.7, 5.9]
          },
          trade_balance_chart: {
            years: [1980, 1985, 1990],
            net_exports: [20.0, 25.0, 35.0]
          },
          consumption_savings_pie: {
            consumption: 800.0,
            savings: 160.0
          }
        }
      };
      
      axios.get.mockResolvedValue(mockResponse);
      
      const result = await apiService.getTeamVisualizations('team1');
      
      expect(axios.get).toHaveBeenCalledWith('/api/results/visualizations/team1');
      expect(result).toEqual(mockResponse.data);
    });
    
    it('should handle API errors', async () => {
      axios.get.mockRejectedValue(new Error('API error'));
      
      await expect(apiService.getTeamVisualizations('team1')).rejects.toThrow('API error');
    });
  });
});
