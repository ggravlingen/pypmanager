import { Box, useTheme } from "@mui/material";
import React from "react";

interface StandardCardProps {
  maxWidth?: string;
  height?: string;
  sx?: object;
  children: React.ReactNode;
}

/**
 * A standard card component that wraps its children with a styled Box.
 * @param props - The properties for the StandardCard component.
 * @param props.maxWidth - The maximum width of the card. Default is "1375px".
 * @param props.height - The height of the card. Default is "700px".
 * @param props.children - The content to be displayed inside the card.
 * @param props.sx - Additional styling to be applied to the Box component.
 * @returns The rendered StandardCard component.
 */
export default function StandardCard({
  maxWidth = "1360px",
  height = "700px",
  children,
  sx,
}: StandardCardProps): JSX.Element {
  const theme = useTheme();

  return (
    <Box
      sx={{
        maxWidth: maxWidth,
        width: "100%",
        height: height ?? "auto",
        marginTop: "10px",
        marginLeft: "12px",
        marginRight: "12px",
        marginBottom: "20px",
        paddingTop: "20px",
        paddingBottom: "0px",
        paddingLeft: "20px",
        paddingRight: "20px",
        borderRadius: "5px",
        boxShadow:
          theme.palette.mode === "dark"
            ? "0 4px 8px rgba(0, 0, 0, 0.5)"
            : "0 4px 8px rgba(0, 0, 0, 0.1)",
        border:
          theme.palette.mode === "dark"
            ? "1px solid rgba(255, 255, 255, 0.1)"
            : "1px solid rgba(0, 0, 0, 0.1)",
        backgroundColor: theme.palette.background.paper,
        color: theme.palette.text.primary,
        ...sx,
      }}
    >
      {children}
    </Box>
  );
}
