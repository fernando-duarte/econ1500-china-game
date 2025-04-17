# Load Testing for China Growth Game

This directory contains a load testing script using [Artillery](https://artillery.io/) to test both HTTP API endpoints and WebSocket real-time features.

## Prerequisites
- [Node.js](https://nodejs.org/) installed
- Artillery installed globally:
  ```
  npm install -g artillery
  ```

## Running the Load Test
1. Make sure your backend server is running locally on `localhost:3000` (adjust the target in the YAML if needed).
2. From the project root, run:
   ```
   artillery run load-testing/artillery-load-test.yml
   ```
3. Artillery will simulate up to 100 users making HTTP requests and WebSocket connections, and print a summary report at the end.

## What This Test Does
- Sends GET requests to key API endpoints:
  - `/api/game/state`
  - `/api/results/rankings`
  - `/api/results/leaderboard`
  - `/api/economic-model/health`
- Opens WebSocket connections to the server, emits `startGame` and `advanceRound` events, and then disconnects.

## Customization
- You can adjust the `arrivalRate`, `rampTo`, and `duration` in `artillery-load-test.yml` to simulate different loads.
- For more advanced scenarios, see the [Artillery documentation](https://www.artillery.io/docs/). 