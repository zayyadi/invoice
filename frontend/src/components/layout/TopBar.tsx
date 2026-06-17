"use client";

import { AppBar, Toolbar, Typography, Box, IconButton, Avatar } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";

export default function TopBar({ onMenuClick }: { onMenuClick?: () => void }) {
  return (
    <AppBar position="sticky" elevation={0}>
      <Toolbar sx={{ justifyContent: "space-between", px: { xs: 2, md: 3 } }}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="Open navigation"
          onClick={onMenuClick}
          sx={{ display: { xs: "inline-flex", md: "none" } }}
        >
          <MenuIcon />
        </IconButton>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <Typography variant="body2" color="text.secondary">
            Dev User
          </Typography>
          <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main", fontSize: 14, fontWeight: 600 }}>
            D
          </Avatar>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
