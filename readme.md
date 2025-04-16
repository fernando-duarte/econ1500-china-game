# China's Growth Game: Saving, Trade, and Prosperity (1980–2025)

An interactive economic simulation game designed for undergraduate economics courses.

## Overview
**Duration**: 50 minutes (10 rounds, each representing 5-year intervals from 1980–2025)  
**Participants**: 80 students divided into 10 teams of 8 students each

## Requirements
- Interactive web UI for student decision-making and data visualization
- Real-time synchronization between student devices and professor dashboard
- Stable Wi-Fi connectivity for up to 80 concurrent users
- Clear and intuitive UI/UX design suitable for classroom settings

## Tech Stack

### Frontend
- React.js: 18.2.0
- Material UI (MUI): 5.15.14
- Chart.js: 4.4.3

### Backend
- Node.js: 20.11.1
- Express.js: 4.19.2
- WebSockets (Socket.IO): 4.7.5

### Economic Model Computations
- Python: 3.12.2
- FastAPI: 0.110.0
- NumPy: 1.26.4
- Pandas: 2.2.2

### Deployment
- Docker: 26.1.4
- AWS/GCP/Azure (Flexible)

## Development Milestones

### Milestone 1: Infrastructure Setup
- Initialize GitHub repository
- Set up Docker container environment
- Establish backend structure (Node.js and Express.js)

### Milestone 2: Economic Model Implementation
- Develop Python microservice with explicit economic model computations
- Validate economic calculations through unit tests
- Ensure microservice integration with backend via API endpoints
- Base on files in Python Solow Model folder, solow_model.py and solow_model_run.py

### Milestone 3: Frontend and UI Design
- Implement interactive decision controls (savings rate slider, exchange rate buttons)
- Design real-time dashboard with countdown timer and economic statistics
- Integrate visualizations (GDP growth, trade balance, consumption vs. savings)
- Build event-driven "Breaking News" UI component

### Milestone 4: Real-time Interactivity
- Set up WebSocket integration for real-time game state synchronization
- Develop Professor Dashboard with real-time ranking and controls for game flow
- Conduct load testing for simultaneous connections (up to 100)

### Milestone 5: Deployment and Testing
- Deploy integrated application to cloud environment
- Perform comprehensive end-to-end testing
- Execute a mock classroom run-through with a smaller test group
- Gather feedback and make necessary adjustments for stability and usability