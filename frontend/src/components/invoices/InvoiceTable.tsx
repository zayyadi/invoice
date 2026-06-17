"use client";

import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Box, Typography, IconButton, TablePagination } from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { useRouter } from "next/navigation";
import type { Invoice } from "@/lib/types";
import StatusChip from "./StatusChip";
import dayjs from "dayjs";

interface Props {
  invoices: Invoice[];
}

export default function InvoiceTable({ invoices }: Props) {
  const router = useRouter();

  return (
    <TableContainer component={Paper} elevation={0}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Invoice #</TableCell>
            <TableCell>Customer</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Due Date</TableCell>
            <TableCell align="right">Amount</TableCell>
            <TableCell align="right">Paid</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {invoices.map((inv) => (
            <TableRow
              key={inv.id}
              hover
              sx={{ cursor: "pointer" }}
              onClick={() => router.push(`/invoices/${inv.id}`)}
            >
              <TableCell>
                <Typography variant="body2" fontWeight={600} color="primary.main">
                  #{inv.invoice_number}
                </Typography>
              </TableCell>
              <TableCell>{inv.customer_name}</TableCell>
              <TableCell sx={{ fontFeatureSettings: '"tnum"' }}>{dayjs(inv.issue_date).format("MMM D, YYYY")}</TableCell>
              <TableCell sx={{ fontFeatureSettings: '"tnum"' }}>{dayjs(inv.due_date).format("MMM D, YYYY")}</TableCell>
              <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"', fontWeight: 600 }}>
                {inv.currency} {inv.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </TableCell>
              <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"', color: inv.paid_amount > 0 ? "success.main" : "text.secondary" }}>
                {inv.currency} {inv.paid_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </TableCell>
              <TableCell>
                <StatusChip status={inv.status} />
              </TableCell>
              <TableCell align="center">
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); router.push(`/invoices/${inv.id}`); }}>
                  <VisibilityIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
