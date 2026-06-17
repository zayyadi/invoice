"use client";

import { useParams, useRouter } from "next/navigation";
import {
  Box, Typography, Card, CardContent, Grid, Button, Divider, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogActions,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { useClient, useClientInvoices, useDeleteClient } from "@/lib/queries";
import StatusChip from "@/components/invoices/StatusChip";
import dayjs from "dayjs";
import { useState } from "react";

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: client, isLoading, error } = useClient(id);
  const { data: invoices } = useClientInvoices(id);
  const deleteClient = useDeleteClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error || !client) return <Alert severity="error">Client not found</Alert>;

  const handleDelete = async () => {
    await deleteClient.mutateAsync(id);
    router.push("/clients");
  };

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton onClick={() => router.back()}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h2" fontWeight={700}>{client.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              Client since {dayjs(client.created_at).format("MMMM YYYY")}
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Button variant="outlined" startIcon={<EditIcon />} onClick={() => router.push(`/clients/${id}/edit`)}>
            Edit
          </Button>
          <Button variant="outlined" color="error" startIcon={<DeleteIcon />} onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => router.push(`/invoices/new`)}>
            New Invoice
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 2 }}>Contact Information</Typography>
              <Grid container spacing={2}>
                {[
                  { label: "Email", value: client.email },
                  { label: "Phone", value: client.phone },
                  { label: "Tax ID", value: client.tax_id },
                  { label: "Currency", value: client.default_currency },
                ].filter((f) => f.value).map((field) => (
                  <Grid item xs={12} sm={6} key={field.label}>
                    <Typography variant="caption" color="text.secondary" sx={{ letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 700 }}>
                      {field.label}
                    </Typography>
                    <Typography fontWeight={500}>{field.value}</Typography>
                  </Grid>
                ))}
                {client.address && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 700 }}>
                      Address
                    </Typography>
                    <Typography fontWeight={500} sx={{ whiteSpace: "pre-line" }}>{client.address}</Typography>
                  </Grid>
                )}
                {client.notes && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 700 }}>
                      Notes
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: "pre-line" }}>{client.notes}</Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 2 }}>Summary</Typography>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Total Invoices</Typography>
                <Typography fontWeight={600}>{invoices?.length || 0}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {invoices && invoices.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h5" sx={{ mb: 2 }}>Invoices</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Invoice #</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {invoices.map((inv) => (
                    <TableRow key={inv.id} hover sx={{ cursor: "pointer" }} onClick={() => router.push(`/invoices/${inv.id}`)}>
                      <TableCell sx={{ fontWeight: 600, color: "primary.main" }}>#{inv.invoice_number}</TableCell>
                      <TableCell>{dayjs(inv.issue_date).format("MMM D, YYYY")}</TableCell>
                      <TableCell>{dayjs(inv.due_date).format("MMM D, YYYY")}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        {inv.currency} {Number(inv.total_amount).toFixed(2)}
                      </TableCell>
                      <TableCell><StatusChip status={inv.status} /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)}>
        <DialogTitle>Delete {client.name}?</DialogTitle>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete} disabled={deleteClient.isPending}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function IconButton({ children, ...props }: any) {
  return <Button {...props} sx={{ minWidth: "auto", p: 1 }}>{children}</Button>;
}
