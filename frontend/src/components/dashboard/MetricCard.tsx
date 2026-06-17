"use client";

import { Card, CardContent, Typography, Box } from "@mui/material";
import type { ReactNode } from "react";

interface Props {
  title: string;
  value: string | number;
  icon: ReactNode;
  color?: string;
  subtitle?: string;
}

export default function MetricCard({ title, value, icon, color = "primary.main", subtitle }: Props) {
  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              {title}
            </Typography>
            <Typography variant="h2" sx={{ mt: 0.5, fontWeight: 700, fontFeatureSettings: '"tnum"' }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: `${color}14`,
              color,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
