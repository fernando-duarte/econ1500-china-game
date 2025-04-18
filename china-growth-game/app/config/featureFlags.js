/**
 * Feature Flags Manager for the China Growth Game
 * 
 * Provides a centralized system for enabling/disabling features 
 * with per-class or per-user granularity.
 */

const dotenv = require('dotenv');
const { getSecret } = require('./secrets');

// Load environment variables
dotenv.config();

// Default feature flag configuration
const DEFAULT_FLAGS = {
  // Events related feature flags
  'events.breakingNews': false,       // Breaking news events feature
  'events.globalShocks': true,        // Global economic shock events
  'events.marketVolatility': true,    // Market volatility events
  'events.wtoAccession': true,        // WTO Accession event in year 2001
  
  // UI related feature flags
  'ui.newDashboardCharts': false,     // Enhanced dashboard charts
  'ui.realTimeUpdates': true,         // Real-time data updates
  'ui.leaderboard': true,             // Leaderboard feature
  'ui.teamComparison': false,         // Team comparison tool
  
  // Game mechanics
  'game.advancedEconomyRules': false, // Advanced economic simulation rules
  'game.competitiveMode': false,      // Competitive game mode
  'game.currencyManipulation': true,  // Currency manipulation mechanics
  'game.crisisEvents': true,          // Economic crisis events
  
  // Admin features
  'admin.roundReset': true,           // Allow resetting rounds
  'admin.manualEvents': false,        // Manual event triggering
  'admin.exportGameData': true,       // Export game data to CSV
};

// Cache for feature flags
let flagsCache = null;
let cacheExpiry = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Loads feature flags from environment, remote source, or defaults
 * @returns {Promise<Object>} The feature flags configuration
 */
async function loadFeatureFlags() {
  // If we have a valid cache, use it
  const now = Date.now();
  if (flagsCache && cacheExpiry > now) {
    return flagsCache;
  }
  
  try {
    // In production, fetch from a remote source
    if (process.env.NODE_ENV === 'production') {
      const remoteFlags = await getSecret('FEATURE_FLAGS', { 
        provider: 'aws', 
        required: false 
      });
      
      if (remoteFlags) {
        try {
          // Parse the JSON string into an object
          const parsedFlags = JSON.parse(remoteFlags);
          // Update cache
          flagsCache = { ...DEFAULT_FLAGS, ...parsedFlags };
          cacheExpiry = now + CACHE_TTL;
          return flagsCache;
        } catch (parseError) {
          console.error('Error parsing remote feature flags:', parseError);
        }
      }
    }
    
    // For development or if remote fetch fails, use environment variables
    const flags = { ...DEFAULT_FLAGS };
    
    // Override with environment variables (FORMAT: FEATURE_FLAG_events_breakingNews=true)
    Object.keys(DEFAULT_FLAGS).forEach(key => {
      const envKey = `FEATURE_FLAG_${key.replace(/\./g, '_')}`;
      if (process.env[envKey] !== undefined) {
        const value = process.env[envKey].toLowerCase();
        flags[key] = value === 'true' || value === '1' || value === 'yes';
      }
    });
    
    // Update cache
    flagsCache = flags;
    cacheExpiry = now + CACHE_TTL;
    return flags;
  } catch (error) {
    console.error('Failed to load feature flags:', error);
    return DEFAULT_FLAGS;
  }
}

/**
 * Determine if a feature is enabled globally
 * @param {string} featureKey - The feature key to check
 * @returns {Promise<boolean>} Whether the feature is enabled
 */
async function isFeatureEnabled(featureKey) {
  const flags = await loadFeatureFlags();
  return !!flags[featureKey];
}

/**
 * Determine if a feature is enabled for a specific team
 * @param {string} featureKey - The feature key to check
 * @param {string} teamId - The team ID
 * @returns {Promise<boolean>} Whether the feature is enabled for this team
 */
async function isFeatureEnabledForTeam(featureKey, teamId) {
  // First check if the feature is globally enabled
  const isGloballyEnabled = await isFeatureEnabled(featureKey);
  
  if (!isGloballyEnabled) {
    // Check if there's a team override
    const overrideKey = `${featureKey}.team.${teamId}`;
    const flags = await loadFeatureFlags();
    return !!flags[overrideKey];
  }
  
  return true;
}

/**
 * Determine if a feature is enabled for a specific class
 * @param {string} featureKey - The feature key to check
 * @param {string} classId - The class ID
 * @returns {Promise<boolean>} Whether the feature is enabled for this class
 */
async function isFeatureEnabledForClass(featureKey, classId) {
  // First check if the feature is globally enabled
  const isGloballyEnabled = await isFeatureEnabled(featureKey);
  
  if (!isGloballyEnabled) {
    // Check if there's a class override
    const overrideKey = `${featureKey}.class.${classId}`;
    const flags = await loadFeatureFlags();
    return !!flags[overrideKey];
  }
  
  return true;
}

/**
 * Gets all enabled features
 * @returns {Promise<Object>} Map of feature keys to boolean values
 */
async function getAllFeatures() {
  return await loadFeatureFlags();
}

/**
 * Manually override a feature flag (admin use only)
 * @param {string} featureKey - The feature key to override
 * @param {boolean} isEnabled - Whether to enable the feature
 * @param {Object} options - Optional parameters like scope (global, team, class) and id
 */
async function overrideFeature(featureKey, isEnabled, options = {}) {
  const { scope = 'global', id = null } = options;
  
  // Determine the full key based on scope
  let fullKey = featureKey;
  if (scope === 'team' && id) {
    fullKey = `${featureKey}.team.${id}`;
  } else if (scope === 'class' && id) {
    fullKey = `${featureKey}.class.${id}`;
  }
  
  // Update the cache
  const flags = await loadFeatureFlags();
  flags[fullKey] = isEnabled;
  flagsCache = flags;
  
  // In production, we would persist this to the remote store
  if (process.env.NODE_ENV === 'production') {
    // This would be implemented to update the remote flags storage
    console.log(`Would update remote feature flag: ${fullKey} = ${isEnabled}`);
  }
  
  return flags;
}

// Invalidate cache
function clearCache() {
  flagsCache = null;
  cacheExpiry = 0;
}

module.exports = {
  isFeatureEnabled,
  isFeatureEnabledForTeam,
  isFeatureEnabledForClass,
  getAllFeatures,
  overrideFeature,
  clearCache,
}; 