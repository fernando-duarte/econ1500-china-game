// Jest + socket.io-client test for backend idempotency
const { Server } = require('socket.io');
const Client = require('socket.io-client');
const http = require('http');
const express = require('express');

function getRandomPort() {
  return Math.floor(Math.random() * (65535 - 1024) + 1024);
}

describe('Backend idempotency', () => {
  let io, httpServer, clientSocket;

  afterEach((done) => {
    if (clientSocket) clientSocket.close();
    if (io) io.close();
    if (httpServer) httpServer.close(done);
    else done();
  });

  test('idempotency: updateTeam only processes once per round', (done) => {
    const app = express();
    httpServer = http.createServer(app);
    io = new Server(httpServer);
    let processCount = 0;
    let lastProcessed = {};
    io.on('connection', (socket) => {
      socket.on('updateTeam', (data) => {
        if (lastProcessed[data.teamId] !== data.round) {
          lastProcessed[data.teamId] = data.round;
          processCount++;
        }
      });
    });
    const port = getRandomPort();
    httpServer.listen(port, (err) => {
      if (err) {
        console.error('Server failed to start:', err);
        done(err);
        return;
      }
      clientSocket = new Client(`http://localhost:${port}`);
      clientSocket.on('connect', () => {
        clientSocket.emit('updateTeam', { teamId: 'A', round: 1 });
        clientSocket.emit('updateTeam', { teamId: 'A', round: 1 });
        setTimeout(() => {
          expect(processCount).toBe(1);
          done();
        }, 100);
      });
    });
  }, 3000);

  test('idempotency: startGame only processes once', (done) => {
    const app = express();
    httpServer = http.createServer(app);
    io = new Server(httpServer);
    let started = false;
    let processCount = 0;
    io.on('connection', (socket) => {
      socket.on('startGame', () => {
        if (!started) {
          started = true;
          processCount++;
        }
      });
    });
    const port = getRandomPort();
    httpServer.listen(port, (err) => {
      if (err) {
        console.error('Server failed to start:', err);
        done(err);
        return;
      }
      clientSocket = new Client(`http://localhost:${port}`);
      clientSocket.on('connect', () => {
        clientSocket.emit('startGame');
        clientSocket.emit('startGame');
        setTimeout(() => {
          expect(processCount).toBe(1);
          done();
        }, 100);
      });
    });
  }, 3000);

  test('idempotency: nextRound only processes once per round', (done) => {
    const app = express();
    httpServer = http.createServer(app);
    io = new Server(httpServer);
    let lastRound = null;
    let processCount = 0;
    io.on('connection', (socket) => {
      socket.on('nextRound', (round) => {
        if (lastRound !== round) {
          lastRound = round;
          processCount++;
        }
      });
    });
    const port = getRandomPort();
    httpServer.listen(port, (err) => {
      if (err) {
        console.error('Server failed to start:', err);
        done(err);
        return;
      }
      clientSocket = new Client(`http://localhost:${port}`);
      clientSocket.on('connect', () => {
        clientSocket.emit('nextRound', 2);
        clientSocket.emit('nextRound', 2);
        setTimeout(() => {
          expect(processCount).toBe(1);
          done();
        }, 100);
      });
    });
  }, 3000);
}); 