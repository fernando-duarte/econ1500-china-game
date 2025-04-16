const axios = require('axios');

class EconomicModelService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl || process.env.ECONOMIC_MODEL_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck() {
    try {
      const response = await this.client.get('/');
      return response.data;
    } catch (error) {
      console.error('Economic model health check failed:', error.message);
      throw error;
    }
  }

  async runSimulation(simulationData) {
    try {
      const response = await this.client.post('/simulate', simulationData);
      return response.data;
    } catch (error) {
      console.error('Economic model simulation failed:', error.message);
      throw error;
    }
  }

  // Default parameters and initial conditions as specified in specs
  getDefaultParameters() {
    return {
      alpha: 0.3,
      delta: 0.1,
      g: 0.005,
      theta: 0.1453,
      phi: 0.1,
      s: 0.2, // Default savings rate, will be changed by students
      beta: -90,
      n: 0.00717,
      eta: 0.02
    };
  }

  getDefaultInitialConditions() {
    return {
      Y: 306.2,
      K: 800,
      L: 600,
      H: 1.0,
      A: 1.0,
      NX: 3.6
    };
  }
}

module.exports = EconomicModelService; 