/**
 * MDBoxRoot Component
 * 
 * Styled component for MDBox with theme-aware styling.
 */

import Box from "@mui/material/Box";
import { styled } from "@mui/material/styles";

export default styled(Box)(({ theme, ownerState }) => {
  const { palette } = theme;
  const { variant, bgColor, color, opacity, borderRadius, shadow, coloredShadow } = ownerState;

  // Define color values
  const backgroundValue = bgColor === "transparent" ? "transparent" : palette[bgColor]?.main || bgColor;
  const colorValue = palette[color]?.main || color;

  return {
    opacity,
    background: backgroundValue,
    color: colorValue,
    borderRadius,
    boxShadow: shadow,
  };
});
