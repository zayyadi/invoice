"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import PeopleIcon from "@mui/icons-material/People";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: <DashboardIcon /> },
  { label: "Invoices", href: "/invoices", icon: <ReceiptLongIcon /> },
  { label: "Clients", href: "/clients", icon: <PeopleIcon /> },
];

interface Props {
  mobile?: boolean;
  onNavigate?: () => void;
}

export default function Sidebar({ mobile = false, onNavigate }: Props) {
  const pathname = usePathname();

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <Box
      sx={{
        width: 260,
        height: "100vh",
        position: mobile ? "relative" : "fixed",
        top: 0,
        left: 0,
        zIndex: 1200,
        display: "flex",
        flexDirection: "column",
        backgroundColor: "rgba(255,248,247,0.95)",
        borderRight: "1px solid",
        borderColor: "divider",
      }}
    >
      <Box sx={{ px: 3, py: 3, display: "flex", alignItems: "center", gap: 1.5 }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1,
            background: "primary.main",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontWeight: 700,
            fontSize: 18,
          }}
        >
          A
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 700, color: "primary.main" }}>
          Aura Invoice
        </Typography>
      </Box>

      <Divider sx={{ mx: 2 }} />

      <List sx={{ flex: 1, px: 1.5, py: 2 }}>
        {NAV_ITEMS.map((item) => {
          const active = isActive(item.href);
          return (
            <ListItem key={item.href} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                component={Link}
                href={item.href}
                onClick={onNavigate}
                sx={{
                  borderRadius: 1,
                  py: 1.25,
                  px: 2,
                  backgroundColor: active ? "rgba(161,53,76,0.08)" : "transparent",
                  "&:hover": { backgroundColor: "rgba(161,53,76,0.05)" },
                }}
              >
                <ListItemIcon sx={{ minWidth: 36, color: active ? "primary.main" : "text.secondary" }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: 14,
                    fontWeight: active ? 600 : 500,
                    color: active ? "primary.main" : "text.secondary",
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Box sx={{ px: 3, py: 2, borderTop: "1px solid", borderColor: "divider" }}>
        <Typography variant="caption" color="text.secondary">
          Aura Invoice v0.1
        </Typography>
      </Box>
    </Box>
  );
}
