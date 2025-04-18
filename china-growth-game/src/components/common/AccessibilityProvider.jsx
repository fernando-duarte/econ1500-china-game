import React, { createContext, useContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

// Create context for accessibility settings
const AccessibilityContext = createContext();

/**
 * Provider component for accessibility features throughout the application
 * Implements WCAG 2.1 AA compliance features
 */
export const AccessibilityProvider = ({ children }) => {
  // Initialize state from localStorage if available
  const [settings, setSettings] = useState(() => {
    const savedSettings = localStorage.getItem('accessibility-settings');
    return savedSettings 
      ? JSON.parse(savedSettings)
      : {
          highContrast: false,
          largeText: false,
          reducedMotion: false,
          screenReader: false,
          focusVisible: true,
        };
  });

  // Save settings to localStorage when changed
  useEffect(() => {
    localStorage.setItem('accessibility-settings', JSON.stringify(settings));
    
    // Apply accessibility classes to document
    const htmlElement = document.documentElement;
    
    if (settings.highContrast) {
      htmlElement.classList.add('high-contrast');
    } else {
      htmlElement.classList.remove('high-contrast');
    }
    
    if (settings.largeText) {
      htmlElement.classList.add('large-text');
    } else {
      htmlElement.classList.remove('large-text');
    }
    
    if (settings.reducedMotion) {
      htmlElement.classList.add('reduced-motion');
    } else {
      htmlElement.classList.remove('reduced-motion');
    }
    
    if (settings.focusVisible) {
      htmlElement.classList.add('focus-visible');
    } else {
      htmlElement.classList.remove('focus-visible');
    }
    
  }, [settings]);

  // Check for prefers-reduced-motion media query
  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    if (prefersReducedMotion.matches) {
      setSettings(prev => ({ ...prev, reducedMotion: true }));
    }
    
    const handleChange = (e) => {
      setSettings(prev => ({ ...prev, reducedMotion: e.matches }));
    };
    
    prefersReducedMotion.addEventListener('change', handleChange);
    return () => prefersReducedMotion.removeEventListener('change', handleChange);
  }, []);

  // Toggle individual settings
  const toggleHighContrast = () => {
    setSettings(prev => ({ ...prev, highContrast: !prev.highContrast }));
  };
  
  const toggleLargeText = () => {
    setSettings(prev => ({ ...prev, largeText: !prev.largeText }));
  };
  
  const toggleReducedMotion = () => {
    setSettings(prev => ({ ...prev, reducedMotion: !prev.reducedMotion }));
  };
  
  const toggleScreenReader = () => {
    setSettings(prev => ({ ...prev, screenReader: !prev.screenReader }));
  };
  
  const toggleFocusVisible = () => {
    setSettings(prev => ({ ...prev, focusVisible: !prev.focusVisible }));
  };

  // Reset to defaults
  const resetToDefaults = () => {
    setSettings({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      screenReader: false,
      focusVisible: true,
    });
  };

  // Context value
  const value = {
    ...settings,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    toggleScreenReader,
    toggleFocusVisible,
    resetToDefaults,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {settings.screenReader && (
        <div className="sr-only" role="status" aria-live="polite">
          Screen reader mode is active
        </div>
      )}
      {children}
    </AccessibilityContext.Provider>
  );
};

AccessibilityProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// Custom hook for using accessibility context
export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}; 