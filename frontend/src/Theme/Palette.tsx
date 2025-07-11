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
  primary: _PaletteColor;
  secondary: _PaletteColor;
  background: {
    default: string;
    paper: string;
  };
  text: {
    primary: string;
    secondary: string;
    disabled: string;
    hint: string;
  };
}

const LightPalette: PaletteOptions = {
  mode: "light",
  primary: {
    main: "#1976d2", // Material-UI default blue
    light: "#42a5f5",
    dark: "#1565c0",
    contrastText: "#ffffff",
  },
  secondary: {
    main: "#dc004e", // Material-UI default pink
    light: "#f06292",
    dark: "#c2185b",
    contrastText: "#ffffff",
  },
  background: {
    default: "#ffffff",
    paper: "#ffffff",
  },
  text: {
    primary: "rgba(0, 0, 0, 0.87)",
    secondary: "rgba(0, 0, 0, 0.6)",
    disabled: "rgba(0, 0, 0, 0.38)",
    hint: "rgba(0, 0, 0, 0.38)",
  },
};

const DarkPalette: PaletteOptions = {
  mode: "dark",
  primary: {
    main: "#90caf9", // Material-UI default light blue for dark mode
    light: "#e3f2fd",
    dark: "#42a5f5",
    contrastText: "rgba(0, 0, 0, 0.87)",
  },
  secondary: {
    main: "#f48fb1", // Material-UI default light pink for dark mode
    light: "#fce4ec",
    dark: "#f06292",
    contrastText: "rgba(0, 0, 0, 0.87)",
  },
  background: {
    default: "#121212",
    paper: "#1e1e1e",
  },
  text: {
    primary: "#ffffff",
    secondary: "rgba(255, 255, 255, 0.7)",
    disabled: "rgba(255, 255, 255, 0.5)",
    hint: "rgba(255, 255, 255, 0.5)",
  },
};

export { LightPalette, DarkPalette };
