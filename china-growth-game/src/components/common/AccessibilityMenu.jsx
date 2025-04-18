import React, { useState } from 'react';
import { useAccessibility } from './AccessibilityProvider';
import {
  Box,
  Button,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Switch,
  Typography,
  Divider,
} from '@mui/material';
import AccessibilityNewIcon from '@mui/icons-material/AccessibilityNew';
import CloseIcon from '@mui/icons-material/Close';
import SettingsBackupRestoreIcon from '@mui/icons-material/SettingsBackupRestore';

/**
 * Accessibility options menu component
 * Provides WCAG 2.1 AA-compliant controls for adjusting accessibility settings
 */
const AccessibilityMenu = () => {
  const [open, setOpen] = useState(false);
  const {
    highContrast,
    largeText,
    reducedMotion,
    screenReader,
    focusVisible,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    toggleScreenReader,
    toggleFocusVisible,
    resetToDefaults,
  } = useAccessibility();

  const toggleDrawer = (isOpen) => () => {
    setOpen(isOpen);
  };

  return (
    <>
      {/* Accessibility toggle button */}
      <IconButton
        aria-label="Open accessibility menu"
        onClick={toggleDrawer(true)}
        color="primary"
        sx={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 1050,
          backgroundColor: 'background.paper',
          boxShadow: 3,
          '&:hover': {
            backgroundColor: 'primary.light',
          },
        }}
      >
        <AccessibilityNewIcon />
      </IconButton>

      {/* Skip to main content link for keyboard users */}
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>

      {/* Accessibility drawer menu */}
      <Drawer
        anchor="right"
        open={open}
        onClose={toggleDrawer(false)}
        aria-labelledby="accessibility-menu-title"
      >
        <Box
          role="presentation"
          sx={{ width: 300, padding: 2 }}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" id="accessibility-menu-title">
              Accessibility Options
            </Typography>
            <IconButton
              aria-label="Close accessibility menu"
              onClick={toggleDrawer(false)}
              size="small"
            >
              <CloseIcon />
            </IconButton>
          </Box>

          <Divider sx={{ my: 2 }} />

          <List>
            <ListItem>
              <ListItemText
                primary="High Contrast"
                secondary="Enhances color contrast for better readability"
                primaryTypographyProps={{ component: 'label', htmlFor: 'high-contrast-switch' }}
              />
              <Switch
                id="high-contrast-switch"
                edge="end"
                onChange={toggleHighContrast}
                checked={highContrast}
                inputProps={{
                  'aria-label': 'Toggle high contrast mode',
                }}
              />
            </ListItem>

            <ListItem>
              <ListItemText
                primary="Large Text"
                secondary="Increases text size for better readability"
                primaryTypographyProps={{ component: 'label', htmlFor: 'large-text-switch' }}
              />
              <Switch
                id="large-text-switch"
                edge="end"
                onChange={toggleLargeText}
                checked={largeText}
                inputProps={{
                  'aria-label': 'Toggle large text mode',
                }}
              />
            </ListItem>

            <ListItem>
              <ListItemText
                primary="Reduced Motion"
                secondary="Minimizes animations and transitions"
                primaryTypographyProps={{ component: 'label', htmlFor: 'reduced-motion-switch' }}
              />
              <Switch
                id="reduced-motion-switch"
                edge="end"
                onChange={toggleReducedMotion}
                checked={reducedMotion}
                inputProps={{
                  'aria-label': 'Toggle reduced motion mode',
                }}
              />
            </ListItem>

            <ListItem>
              <ListItemText
                primary="Screen Reader Announcements"
                secondary="Provides additional context for screen readers"
                primaryTypographyProps={{ component: 'label', htmlFor: 'screen-reader-switch' }}
              />
              <Switch
                id="screen-reader-switch"
                edge="end"
                onChange={toggleScreenReader}
                checked={screenReader}
                inputProps={{
                  'aria-label': 'Toggle screen reader announcements',
                }}
              />
            </ListItem>

            <ListItem>
              <ListItemText
                primary="Focus Indicators"
                secondary="Makes keyboard focus more visible"
                primaryTypographyProps={{ component: 'label', htmlFor: 'focus-visible-switch' }}
              />
              <Switch
                id="focus-visible-switch"
                edge="end"
                onChange={toggleFocusVisible}
                checked={focusVisible}
                inputProps={{
                  'aria-label': 'Toggle focus indicators',
                }}
              />
            </ListItem>
          </List>

          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <Button
              startIcon={<SettingsBackupRestoreIcon />}
              onClick={resetToDefaults}
              aria-label="Reset accessibility settings to defaults"
              variant="outlined"
            >
              Reset to Defaults
            </Button>
          </Box>
        </Box>
      </Drawer>
    </>
  );
};

export default AccessibilityMenu; 