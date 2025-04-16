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
- **Frontend**: React.js with Material UI for responsive, intuitive interface
- **Backend**: Node.js and Express.js for real-time data handling
- **Real-time communication**: WebSockets (Socket.IO)
- **Economic model computations**: Python (FastAPI) microservice
- **Deployment**: Docker containers hosted on cloud (AWS/GCP/Azure)

## Development Milestones

### Milestone 1: Infrastructure Setup
- Initialize GitHub repository
- Set up Docker container environment
- Establish backend structure (Node.js and Express.js)

### Milestone 2: Economic Model Implementation
- Develop Python microservice with explicit economic model computations
- Validate economic calculations through unit tests
- Ensure microservice integration with backend via API endpoints

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

