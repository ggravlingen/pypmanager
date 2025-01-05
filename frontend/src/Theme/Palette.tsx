import type { PaletteOptions as _PaletteOptions } from "@mui/material";

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

/**
 * Extends the Material-UI PaletteOptions interface to include a custom definition for the primary color.
 * Inherits properties from Material-UI's PaletteOptions.
 */
interface PaletteOptions extends _PaletteOptions {
  /**
   * Defines the primary color of the palette.
   * The type for defining the primary color, including main, light, dark, and contrastText shades.
   */
  // common: CommonColors;
  primary: _PaletteColor;
  secondary: _PaletteColor;
  background: {
    default: string;
    paper: string;
  };
  surface: {
    default: string;
  };
  text: {
    primary: string;
    secondary: string;
    disabled: string;
    hint: string;
  };
}

export const LightPalette: PaletteOptions = {
  mode: "light",
  primary: {
    main: "#005f99",
    light: "#3a7bc1",
    dark: "#003f66",
    contrastText: "#ffffff",
  },
  secondary: {
    main: "#adb5bd",
    light: "#d3d9df",
    dark: "#7b838b",
    contrastText: "#000000",
  },
  background: {
    default: "#f8f9fa",
    paper: "#ffffff",
  },
  surface: {
    default: "#ffffff",
  },
  error: {
    main: "#d00000",
    light: "#ff5f5f",
    dark: "#9b0000",
    contrastText: "#ffffff",
  },
  text: {
    primary: "#000000",
    secondary: "#495057",
    disabled: "#adb5bd",
    hint: "#6c757d",
  },
};

export const DarkPalette: PaletteOptions = {
  mode: "dark",
  primary: {
    main: "#2d6a4f", // Dark Green
    light: "#52b788", // Lighter Green for hover states
    dark: "#1b4332", // Darker Green for depth
    contrastText: "#ffffff",
  },
  secondary: {
    main: "#7b838b",
    light: "#a1a9b0",
    dark: "#52575d",
    contrastText: "#ffffff",
  },
  background: {
    default: "#121212",
    paper: "#1e1e1e",
  },
  surface: {
    default: "#1e1e1e",
  },
  error: {
    main: "#ff5f5f",
    light: "#ff9d9d",
    dark: "#d00000",
    contrastText: "#000000",
  },
  text: {
    primary: "#ffffff",
    secondary: "#b0b0b0",
    disabled: "#757575",
    hint: "#9e9e9e",
  },
};
