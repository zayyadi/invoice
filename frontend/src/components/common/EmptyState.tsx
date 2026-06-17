"use client";

import { Box, Typography, Button } from "@mui/material";
import type { ReactNode } from "react";

interface Props {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export default function EmptyState({ icon, title, description, action }: Props) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        py: 10,
        textAlign: "center",
      }}
    >
      {icon && (
        <Box sx={{ mb: 2, color: "text.secondary", "& svg": { fontSize: 64 } }}>
          {icon}
        </Box>
      )}
      <Typography variant="h3" sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        {description}
      </Typography>
      {action && (
        <Button variant="contained" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </Box>
  );
}
