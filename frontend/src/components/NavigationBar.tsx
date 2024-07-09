import React from "react";
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  IconButton,
  ListItemText,
} from "@mui/material";
import { Dataset, Menu, MenuOpen } from "@mui/icons-material";

const ExpandedNavigationBarWidth = 240;
const CollapsedNavigationBarWidth = 40;

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
        },
      }}
    >
      <List sx={{ padding: 0 }}>
        <ListItem
          onClick={toggleDrawer}
          sx={{
            paddingTop: "0px",
            paddingLeft: "0px",
            paddingBottom: "0px",
            paddingRight: "0px",
          }}
        >
          <ListItemIcon>
            <IconButton aria-label="menu">
              {isExpanded ? <MenuOpen /> : <Menu />}
            </IconButton>
          </ListItemIcon>
          {isExpanded && <ListItemText primary="Portfolio Manager" />}
        </ListItem>
        <ListItem
          sx={{
            paddingTop: "0px",
            paddingLeft: "0px",
            paddingBottom: "0px",
            paddingRight: "0px",
          }}
        >
          <ListItemIcon>
            <IconButton aria-label="home">
              <Dataset />
            </IconButton>
          </ListItemIcon>
          {isExpanded && <ListItemText primary="General ledger" />}
        </ListItem>
      </List>
    </Drawer>
  );
}
