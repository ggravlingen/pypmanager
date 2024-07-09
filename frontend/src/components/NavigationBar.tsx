import { Dataset, Menu, MenuOpen } from "@mui/icons-material";
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

/**
 * Defines the properties for the NavigationItem component.
 * toggleDrawer - A function to toggle the navigation drawer's open/closed state.
 * isExpanded - Indicates whether the navigation drawer is currently expanded.
 * label - The text label for the navigation item.
 * icon - The icon component to display alongside the label.
 */
interface NavigationItemProps {
  toggleDrawer: () => void;
  isExpanded: boolean;
  label: string;
  icon: ReactElement;
}

/**
 * NavigationItem component that renders a single item in the navigation bar.
 *
 * This component displays an icon button and a text label. The icon and label are
 * controlled by the `icon` and `label` props respectively. The `toggleDrawer` function
 * is called when the item is clicked, allowing the parent component to handle the state change.
 * The visibility of the label is controlled by the `isExpanded` prop.
 * @param props - The properties passed to the component.
 * @param props.toggleDrawer - A function to toggle the navigation drawer's open/closed state.
 * @param props.isExpanded - Indicates whether the navigation drawer is currently expanded.
 * @param props.label - The text label for the navigation item.
 * @param props.icon - The icon component to display alongside the label.
 * @returns The NavigationItem component.
 */
function NavigationItem({
  toggleDrawer,
  isExpanded,
  label,
  icon,
}: NavigationItemProps): JSX.Element {
  return (
    <ListItem
      onClick={toggleDrawer}
      sx={{
        paddingTop: "0px",
        paddingLeft: "0px",
        paddingBottom: "0px",
        paddingRight: "0px",
      }}
    >
      <ListItemIcon sx={{ minWidth: "50px" }}>
        <IconButton aria-label="menu">{icon}</IconButton>
      </ListItemIcon>
      {isExpanded && <ListItemText primary={label} />}
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
          toggleDrawer={toggleDrawer}
          isExpanded={isExpanded}
          label={"Portfolio Manager"}
          icon={isExpanded ? <MenuOpen /> : <Menu />}
        />
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          <ListItem
            sx={{
              paddingTop: "0px",
              paddingLeft: "0px",
              paddingBottom: "0px",
              paddingRight: "0px",
            }}
          >
            <ListItemIcon sx={{ minWidth: "50px" }}>
              <IconButton aria-label="home">
                <Dataset />
              </IconButton>
            </ListItemIcon>
            {isExpanded && <ListItemText primary="General ledger" />}
          </ListItem>
        </Link>
      </List>
    </Drawer>
  );
}
