import { Box } from "@mui/material";
import React from "react";

interface StandardCardProps {
  width?: string;
  height?: string;
  sx?: object;
  children: React.ReactNode;
}

/**
 * A standard card component that wraps its children with a styled Box.
 * @param props - The properties for the StandardCard component.
 * @param props.width - The width of the card. Default is "1200px".
 * @param props.height - The height of the card. Default is "700px".
 * @param props.children - The content to be displayed inside the card.
 * @param props.sx - Additional styling to be applied to the Box component.
 * @returns The rendered StandardCard component.
 */
export default function StandardCard({
  width = "1350px",
  height = "700px",
  children,
  sx,
}: StandardCardProps): JSX.Element {
  return (
    <Box
      sx={{
        width: width,
        height: height ?? "auto",
        marginTop: "10px",
        marginLeft: "20px",
        marginRight: "20px",
        marginBottom: "20px",
        paddingTop: "20px",
        paddingBottom: "0px",
        paddingLeft: "20px",
        paddingRight: "20px",
        borderRadius: "16px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        border: "1px solid rgba(0, 0, 0, 0.1)",
        ...sx,
      }}
    >
      {children}
    </Box>
  );
}
