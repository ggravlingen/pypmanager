import { PaletteOptions as _PaletteOptions } from "@mui/material";

/**
 * Represents the color shades in a palette.
 *
 * This interface defines the structure for color shades used within a UI theme,
 * including light, main, dark variants, and a contrast text color for accessibility.
 * light - The lighter variant of the color.
 * main - The main color value, used as the primary color in UI components.
 * dark - The darker variant of the color.
 * contrastText - The color used for text that appears over the main color for better readability.
 */
interface _PaletteColor {
  light: string;
  main: string;
  dark: string;
  contrastText: string;
}

interface CommonColors {
  black: string;
  white: string;
}

/**
 * Extends the Material-UI PaletteOptions interface to include a custom definition for the primary color.
 * Inherits properties from Material-UI's PaletteOptions.
 */
interface PaletteOptions extends _PaletteOptions {
  /**
   * Defines the primary color of the palette.
   * The type for defining the primary color, including main, light, dark, and contrastText shades.
   */
  common: CommonColors;
  primary: _PaletteColor;
}

export const LightPalette: PaletteOptions = {
  mode: "light",
  background: {
    default: "#ffffff",
    paper: "#fff",
  },
  common: {
    black: "#000",
    white: "#fff",
  },
  primary: {
    main: "#1976d2",
    light: "#42a5f5",
    dark: "#1565c0",
    contrastText: "#ffffff",
  },
};

export const DarkPalette: PaletteOptions = {
  mode: "dark",
  background: {
    default: "#121212",
    paper: "#1D1D1D",
  },
  common: {
    black: "#121212",
    white: "#e0e0e0",
  },
  primary: {
    main: "#0A0A0A",
    light: "#e3f2fd",
    dark: "#42a5f5",
    contrastText: "#000",
  },
  secondary: {
    main: "#1F1F1F",
  },
  text: {
    primary: "#FFFFFF",
    secondary: "#B0B0B0",
  },
  divider: "#2D2D2D",
};
