"use client";

import { useState } from "react";
import { Box, Drawer } from "@mui/material";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Box sx={{ display: { xs: "none", md: "block" } }}>
        <Sidebar />
      </Box>
      <Drawer
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { xs: "block", md: "none" }, "& .MuiDrawer-paper": { width: 260 } }}
      >
        <Sidebar mobile onNavigate={() => setMobileOpen(false)} />
      </Drawer>
      <Box sx={{ flex: 1, ml: { xs: 0, md: "260px" }, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <TopBar onMenuClick={() => setMobileOpen(true)} />
        <Box component="main" sx={{ flex: 1, px: { xs: 2, sm: 3, md: 5 }, py: { xs: 3, md: 5 }, maxWidth: 1200, width: "100%", mx: "auto" }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
