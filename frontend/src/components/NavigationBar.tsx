import React, { ReactElement } from "react";
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  IconButton,
  ListItemText,
} from "@mui/material";
import { Dataset, Menu, MenuOpen } from "@mui/icons-material";
import { Link } from "react-router-dom";

const ExpandedNavigationBarWidth = 210;
const CollapsedNavigationBarWidth = 40;

/**
 * Interface defining the properties for NavigationItem component.
 *
 * @interface
 * @property {Function} toggleDrawer - Function to toggle the drawer open or closed.
 * @property {boolean} isExpanded - State indicating if the navigation item is expanded.
 * @property {string} label - Text label for the navigation item.
 * @property {ReactElement} icon - Icon to be displayed alongside the label.
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
 *
 * @param {NavigationItemProps} props - The properties passed to the component.
 * @returns {JSX.Element} The NavigationItem component.
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
