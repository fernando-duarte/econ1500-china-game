const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment variables
dotenv.config();

// Get environment
const NODE_ENV = process.env.NODE_ENV || 'development';

// Function to get secrets from HashiCorp Vault
async function getFromVault(secretPath) {
  // Only attempt to connect to Vault in production/staging
  if (NODE_ENV === 'development' || NODE_ENV === 'test') {
    return null;
  }
  
  try {
    // This would be replaced with actual Vault SDK integration
    // const vault = require('node-vault')({
    //   apiVersion: 'v1',
    //   endpoint: process.env.VAULT_ADDR,
    //   token: process.env.VAULT_TOKEN
    // });
    // const result = await vault.read(secretPath);
    // return result.data;
    console.log(`[PROD] Would fetch ${secretPath} from Vault`);
    return null;
  } catch (error) {
    console.error(`Error fetching secret from Vault: ${error.message}`);
    return null;
  }
}

// Function to get secrets from AWS Secrets Manager
async function getFromAWS(secretName) {
  // Only attempt to connect to AWS in production/staging
  if (NODE_ENV === 'development' || NODE_ENV === 'test') {
    return null;
  }
  
  try {
    // This would be replaced with actual AWS SDK integration
    // const AWS = require('aws-sdk');
    // const secretsManager = new AWS.SecretsManager({
    //   region: process.env.AWS_REGION || 'us-east-1'
    // });
    // const result = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
    // return JSON.parse(result.SecretString);
    console.log(`[PROD] Would fetch ${secretName} from AWS Secrets Manager`);
    return null;
  } catch (error) {
    console.error(`Error fetching secret from AWS: ${error.message}`);
    return null;
  }
}

/**
 * Get a secret from the appropriate source based on environment
 * In development: returns from .env file
 * In production: fetches from secret manager (Vault or AWS)
 */
async function getSecret(key, options = {}) {
  const { 
    required = false, 
    default: defaultValue = null,
    provider = 'env' // 'env', 'vault', or 'aws'
  } = options;
  
  // For development/test, always return from environment variables
  if (NODE_ENV === 'development' || NODE_ENV === 'test') {
    const value = process.env[key] || defaultValue;
    if (required && !value) {
      throw new Error(`Required secret ${key} not found in environment`);
    }
    return value;
  }
  
  // For production, attempt to get from secret manager
  let secret = null;
  
  if (provider === 'vault') {
    const vaultPath = options.vaultPath || `solow-game/${key}`;
    secret = await getFromVault(vaultPath);
  } else if (provider === 'aws') {
    const secretName = options.secretName || `solow-game-${key}`;
    secret = await getFromAWS(secretName);
  }
  
  // Fall back to environment variable if not found in secret manager
  if (!secret) {
    secret = process.env[key] || defaultValue;
  }
  
  if (required && !secret) {
    throw new Error(`Required secret ${key} not found`);
  }
  
  return secret;
}

module.exports = {
  getSecret,
  // Helper function to get all secrets for a service
  getServiceSecrets: async (serviceName) => {
    if (NODE_ENV === 'production') {
      // In production, fetch from secret manager
      return await getFromAWS(`solow-game-${serviceName}`) ||
             await getFromVault(`solow-game/${serviceName}`) ||
             {};
    } else {
      // In development, load from .env
      return {};
    }
  }
}; 