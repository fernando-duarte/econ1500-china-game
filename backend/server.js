/**
 * Server Wrapper
 *
 * This file is a wrapper around the main server implementation.
 * It redirects to the main server.
 *
 * For new development, use the server.js directly.
 */

const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const { Server } = require('socket.io');
const axios = require('axios');
require('dotenv').config();

// Redirect to main server
console.log('Forwarding to main server');
// Load the main server directly
require('../server');
// This process will exit as the main server takes over
process.exit(0);

