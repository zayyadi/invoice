"use client";

import { Box, Typography, Button } from "@mui/material";
import type { ReactNode } from "react";

interface Props {
  title: string;
  subtitle?: string;
  action?: { label: string; icon?: ReactNode; onClick: () => void; disabled?: boolean };
}

export default function PageHeader({ title, subtitle, action }: Props) {
  return (
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 4, gap: 2, flexDirection: { xs: "column", sm: "row" } }}>
      <Box>
        <Typography variant="h2" sx={{ fontWeight: 700 }}>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && (
        <Button variant="contained" startIcon={action.icon} onClick={action.onClick} disabled={action.disabled} sx={{ width: { xs: "100%", sm: "auto" } }}>
          {action.label}
        </Button>
      )}
    </Box>
  );
}
