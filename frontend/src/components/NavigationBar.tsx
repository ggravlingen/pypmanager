import {
  AccountBalance,
  DarkMode,
  Dataset,
  LightMode,
  Menu,
  MenuOpen,
} from "@mui/icons-material";
import {
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import React, { ReactElement } from "react";
import { Link } from "react-router-dom";

const ExpandedNavigationBarWidth = 210;
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
  // Conditionally render the ListItem as a link if the `to` prop is provided
  const content = (
    <>
      <ListItemIcon sx={{ minWidth: "50px" }}>
        <IconButton aria-label={label}>{icon}</IconButton>
      </ListItemIcon>
      {isExpanded && <ListItemText primary={label} />}
    </>
  );

  return (
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
  );
}

/**
 * NavigationBar component that renders the application's navigation bar.
 *
 * This component uses a Drawer from Material-UI to create a sidebar that can be
 * collapsed or expanded. The state `isExpanded` controls the width of the Drawer,
 * allowing for a more flexible UI. The `toggleDrawer` function toggles this state,
 * effectively collapsing or expanding the navigation bar.
 *
 * Inside the Drawer, a List component is used to render individual navigation items.
 * The first item is a custom `NavigationItem` component that toggles the Drawer's state.
 * Additional items can be added as `ListItem` components wrapped in `Link` components
 * for navigation. The `ListItemIcon` and `ListItemText` components are used to render
 * the icons and labels for each navigation item, respectively.
 * @returns The NavigationBar component with collapsible behavior and navigation links.
 */
export default function NavigationBar() {
  // State to control the collapse/expand behavior
  const [isExpanded, setIsExpanded] = React.useState(false);

  const [mode, setMode] = React.useState("light");

  // Control the dark mode state
  const toggleDarkMode = () => {
    setMode(mode === "light" ? "dark" : "light");
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
          icon={isExpanded ? <MenuOpen /> : <Menu />}
        />
        <NavigationItem
          handleClick={toggleDarkMode}
          isExpanded={isExpanded}
          label={"Dark mode"}
          icon={mode === "dark" ? <DarkMode /> : <LightMode />}
        />
        <NavigationItem
          isExpanded={isExpanded}
          label={"Current portfolio"}
          icon={<AccountBalance />}
          linkTo="/"
        />
        <NavigationItem
          isExpanded={isExpanded}
          label={"General ledger"}
          icon={<Dataset />}
          linkTo="/ledger"
        />
      </List>
    </Drawer>
  );
}
