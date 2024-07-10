import {
  AccountBalance,
  DarkMode,
  Dataset,
  LightMode,
  Menu,
  MenuOpen,
  ShowChart,
} from "@mui/icons-material";
import {
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  PaletteMode,
  Tooltip,
} from "@mui/material";
import React, { ReactElement } from "react";
import { Link } from "react-router-dom";

const ExpandedNavigationBarWidth = 185;
const CollapsedNavigationBarWidth = 40;
const ListItemSx = {
  paddingTop: "0px",
  paddingLeft: "0px",
  paddingBottom: "0px",
  paddingRight: "0px",
};

/**
 * Defines the properties for the NavigationItem component.
 * toggleDrawer - A function to toggle the navigation drawer's open/closed state.
 * isExpanded - Indicates whether the navigation drawer is currently expanded.
 * label - The text label for the navigation item.
 * icon - The icon component to display alongside the label.
 * to - The target URL for the navigation item. If provided, the item will be a Link component.
 */
interface NavigationItemProps {
  handleClick?: () => void;
  isExpanded: boolean;
  label: string;
  icon: ReactElement;
  linkTo?: string;
}

/**
 * NavigationItem component that renders a single item in the navigation bar.
 *
 * This component displays an icon button and a text label. The icon and label are
 * controlled by the `icon` and `label` props respectively. The `toggleDrawer` function
 * is called when the item is clicked, allowing the parent component to handle the state change.
 * The visibility of the label is controlled by the `isExpanded` prop.
 * @param props - The properties passed to the component.
 * @param props.handleClick - A function to toggle the navigation drawer's open/closed state.
 * @param props.isExpanded - Indicates whether the navigation drawer is currently expanded.
 * @param props.label - The text label for the navigation item.
 * @param props.icon - The icon component to display alongside the label.
 * @param props.linkTo - The target URL for the navigation item.
 * @returns The NavigationItem component.
 */
function NavigationItem({
  handleClick,
  isExpanded,
  label,
  icon,
  linkTo,
}: NavigationItemProps): JSX.Element {
  const constTooltipLabel =
    label === "Portfolio Manager" ? "Open navigation" : label;

  const content = (
    <>
      <ListItemIcon sx={{ minWidth: "35px" }}>
        <IconButton aria-label={label}>{icon}</IconButton>
      </ListItemIcon>
      {isExpanded && <ListItemText primary={label} />}
    </>
  );

  return (
    <Tooltip title={constTooltipLabel} placement="right" arrow>
      <ListItem onClick={handleClick} sx={ListItemSx}>
        {linkTo ? (
          <Link
            to={linkTo}
            style={{
              textDecoration: "none",
              color: "inherit",
              display: "flex",
              alignItems: "center",
              width: "100%",
            }}
          >
            {content}
          </Link>
        ) : (
          content
        )}
      </ListItem>
    </Tooltip>
  );
}

interface NavigationBarProps {
  colorMode: string;
  setColorMode: React.Dispatch<React.SetStateAction<PaletteMode>>;
}

/**
 * Represents the navigation bar component of the application.
 *
 * This component is responsible for rendering the navigation bar, which includes
 * functionality for toggling the color mode of the application (e.g., light or dark mode).
 * @param props The props passed to the NavigationBar component.
 * @param props.colorMode The current color mode of the application.
 * @param props.setColorMode A function to set the color mode of the application.
 * @returns The NavigationBar component.
 */
export default function NavigationBar({
  colorMode,
  setColorMode,
}: NavigationBarProps) {
  // State to control the collapse/expand behavior
  const [isExpanded, setIsExpanded] = React.useState(false);

  const IconSX =
    colorMode === "light"
      ? { color: `primary.main` }
      : { color: `primary.contrastText` };

  // Control the dark mode state
  const toggleDarkMode = () => {
    const newColorMode = colorMode === "light" ? "dark" : "light";

    setColorMode(newColorMode);
    localStorage.setItem("colorMode", newColorMode);
  };

  // Function to toggle the collapse/expand state
  const toggleDrawer = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: isExpanded
          ? ExpandedNavigationBarWidth
          : CollapsedNavigationBarWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: isExpanded
            ? ExpandedNavigationBarWidth
            : CollapsedNavigationBarWidth,
          boxSizing: "border-box",
          overflowX: "hidden", // Add this line to hide horizontal scrollbar
        },
      }}
    >
      <List sx={{ padding: 0 }}>
        <NavigationItem
          handleClick={toggleDrawer}
          isExpanded={isExpanded}
          label={"Portfolio Manager"}
          icon={isExpanded ? <MenuOpen sx={IconSX} /> : <Menu sx={IconSX} />}
        />
        <NavigationItem
          handleClick={toggleDarkMode}
          isExpanded={isExpanded}
          label={
            colorMode === "dark" ? "Toggle light mode" : "Toggle dark mode"
          }
          icon={
            colorMode === "dark" ? (
              <DarkMode sx={IconSX} />
            ) : (
              <LightMode sx={IconSX} />
            )
          }
        />
        <NavigationItem
          isExpanded={isExpanded}
          label={"Current portfolio"}
          icon={<AccountBalance sx={IconSX} />}
          linkTo="/"
        />
        <NavigationItem
          isExpanded={isExpanded}
          label={"Historical portfolio"}
          icon={<ShowChart sx={IconSX} />}
          linkTo="/history"
        />
        <NavigationItem
          isExpanded={isExpanded}
          label={"General ledger"}
          icon={<Dataset sx={IconSX} />}
          linkTo="/ledger"
        />
      </List>
    </Drawer>
  );
}
