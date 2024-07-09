import { PaletteOptions as _PaletteOptions } from "@mui/material";

/**
 * Represents the color shades in a palette.
 *
 * This interface defines the structure for color shades used within a UI theme,
 * including light, main, dark variants, and a contrast text color for accessibility.
 *
 * @interface _PaletteColor
 * @property {string} light - The lighter variant of the color.
 * @property {string} main - The main color value, used as the primary color in UI components.
 * @property {string} dark - The darker variant of the color.
 * @property {string} contrastText - The color used for text that appears over the main color for better readability.
 */
interface _PaletteColor {
  light: string;
  main: string;
  dark: string;
  contrastText: string;
}

/**
 * Extends the Material-UI PaletteOptions interface to include a custom definition for the primary color.
 *
 * @interface PaletteOptions
 * @extends {_PaletteOptions} Inherits properties from Material-UI's PaletteOptions.
 */
interface PaletteOptions extends _PaletteOptions {
  /**
   * Defines the primary color of the palette.
   *
   * @type {_PaletteColor} The type for defining the primary color, including main, light, dark, and contrastText shades.
   */
  primary: _PaletteColor;
}

const Palette: PaletteOptions = {
  primary: {
    main: "#1976d2",
    light: "#42a5f5",
    dark: "#1565c0",
    contrastText: "#ffffff",
  },
};

export default Palette;
