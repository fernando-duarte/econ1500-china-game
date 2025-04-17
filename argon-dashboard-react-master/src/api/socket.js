import { io } from 'socket.io-client';

/**
 * socket.js
 * Utility for a shared Socket.IO connection and event helpers.
 * Replace SOCKET_URL with your backend WebSocket endpoint.
 */

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:4000'; // TODO: update as needed
let socket;

export function getSocket() {
  if (!socket) {
    socket = io(SOCKET_URL, { transports: ['websocket'] });
  }
  return socket;
}

/**
 * Subscribe to a socket event
 * @param {string} event - Event name
 * @param {function} handler - Event handler
 */
export function on(event, handler) {
  getSocket().on(event, handler);
}

/**
 * Unsubscribe from a socket event
 * @param {string} event - Event name
 * @param {function} handler - Event handler
 */
export function off(event, handler) {
  getSocket().off(event, handler);
}

/**
 * Emit a socket event
 * @param {string} event - Event name
 * @param {any} data - Data to send
 */
export function emit(event, data) {
  getSocket().emit(event, data);
} 