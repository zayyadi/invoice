"use client";

import { Card, CardContent, Typography, Box } from "@mui/material";
import { BarChart } from "@mui/x-charts/BarChart";

interface Props {
  data: { month: string; revenue: number }[];
}

export default function RevenueChart({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Monthly Revenue
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No revenue data yet
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const months = data.map((d) => {
    const [y, m] = d.month.split("-");
    return new Date(Number(y), Number(m) - 1).toLocaleString("en", { month: "short" });
  });
  const values = data.map((d) => d.revenue);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Monthly Revenue
        </Typography>
        <Box sx={{ height: 250 }}>
          <BarChart
            xAxis={[{ data: months, scaleType: "band" }]}
            yAxis={[{}]}
            series={[{ data: values, color: "#a1354c", label: "Revenue" }]}
            height={250}
            margin={{ left: 60, right: 20, top: 10, bottom: 30 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
}
