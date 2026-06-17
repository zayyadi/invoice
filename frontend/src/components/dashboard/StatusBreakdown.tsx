"use client";

import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Box } from "@mui/material";

interface Props {
  breakdown: Record<string, { count: number; total: number; paid: number }>;
}

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  sent: "Sent",
  viewed: "Viewed",
  partial: "Partial",
  paid: "Paid",
  overdue: "Overdue",
  cancelled: "Cancelled",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "#897173",
  sent: "#a1354c",
  viewed: "#0277bd",
  partial: "#e6a817",
  paid: "#36645c",
  overdue: "#ba1a1a",
  cancelled: "#897173",
};

export default function StatusBreakdown({ breakdown }: Props) {
  const rows = Object.entries(breakdown).filter(([, v]) => v.count > 0);

  if (rows.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Invoice Status
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No invoices yet
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Invoice Status
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Status</TableCell>
                <TableCell align="right">Count</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map(([status, data]) => (
                <TableRow key={status}>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box sx={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: STATUS_COLORS[status] }} />
                      <Typography variant="body2" fontWeight={500}>
                        {STATUS_LABELS[status]}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"' }}>
                    {data.count}
                  </TableCell>
                  <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"' }}>
                    NGN {data.total.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
