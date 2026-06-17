"use client";

import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, IconButton, Box } from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { useRouter } from "next/navigation";
import type { ClientListItem } from "@/lib/types";

interface Props {
  clients: ClientListItem[];
}

export default function ClientTable({ clients }: Props) {
  const router = useRouter();

  return (
    <TableContainer component={Paper} elevation={0}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Phone</TableCell>
            <TableCell align="right">Invoices</TableCell>
            <TableCell align="right">Total Invoiced</TableCell>
            <TableCell align="right">Total Paid</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {clients.map((client) => (
            <TableRow
              key={client.id}
              hover
              sx={{ cursor: "pointer" }}
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              <TableCell>
                <Typography variant="body2" fontWeight={600}>
                  {client.name}
                </Typography>
              </TableCell>
              <TableCell>{client.email || "—"}</TableCell>
              <TableCell>{client.phone || "—"}</TableCell>
              <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"' }}>
                {client.invoice_count}
              </TableCell>
              <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"', fontWeight: 600 }}>
                {client.default_currency || "NGN"} {client.total_invoiced}
              </TableCell>
              <TableCell align="right" sx={{ fontFeatureSettings: '"tnum"', color: "success.main" }}>
                {client.default_currency || "NGN"} {client.total_paid}
              </TableCell>
              <TableCell align="center">
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); router.push(`/clients/${client.id}`); }}>
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
