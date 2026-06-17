"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Box, Typography, Grid, Button, Divider, IconButton, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Alert, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Card, CardContent, List, ListItem, ListItemText,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SendIcon from "@mui/icons-material/Send";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DownloadIcon from "@mui/icons-material/Download";
import ShareIcon from "@mui/icons-material/Share";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  useInvoice, useSendInvoice,
  useInvoiceHistory, useInvoicePayments, useUploadLogo, useCreatePayment,
} from "@/lib/queries";
import type { InvoiceStatus } from "@/lib/types";
import StatusChip from "./StatusChip";
import ExportDialog from "./ExportDialog";
import dayjs from "dayjs";

export default function InvoiceDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: invoice, isLoading, error } = useInvoice(id);
  const { data: history } = useInvoiceHistory(id);
  const { data: payments } = useInvoicePayments(id);
  const sendInvoice = useSendInvoice(id);
  const uploadLogo = useUploadLogo();
  const createPayment = useCreatePayment();

  const [exportOpen, setExportOpen] = useState(false);
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [paymentForm, setPaymentForm] = useState({ amount: "", payment_method: "bank_transfer", reference_number: "", notes: "" });

  if (isLoading) return <Typography>Loading...</Typography>;
  if (error || !invoice) return <Alert severity="error">Invoice not found</Alert>;

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await uploadLogo.mutateAsync({ id, file });
  };

  const handleRecordPayment = async () => {
    if (!paymentForm.amount) return;
    await createPayment.mutateAsync({
      invoice_id: id,
      amount: parseFloat(paymentForm.amount),
      payment_method: paymentForm.payment_method,
      reference_number: paymentForm.reference_number || undefined,
      notes: paymentForm.notes || undefined,
    });
    setPaymentOpen(false);
    setPaymentForm({ amount: "", payment_method: "bank_transfer", reference_number: "", notes: "" });
  };

  const outstanding = invoice.total_amount - invoice.paid_amount;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton onClick={() => router.back()}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h2" sx={{ fontWeight: 700 }}>
              #{invoice.invoice_number}
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mt: 0.5 }}>
              <StatusChip status={invoice.status as InvoiceStatus} />
              <Typography variant="body2" color="text.secondary">
                Created {dayjs(invoice.created_at).format("MMM D, YYYY")}
              </Typography>
            </Box>
          </Box>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          {invoice.status === "draft" && (
            <Button variant="contained" startIcon={<SendIcon />} onClick={() => sendInvoice.mutate()} disabled={sendInvoice.isPending}>
              Send
            </Button>
          )}
          {invoice.status !== "paid" && invoice.status !== "cancelled" && (
            <Button variant="outlined" startIcon={<CheckCircleIcon />} onClick={() => setPaymentOpen(true)}>
              Record Payment
            </Button>
          )}
          <Button variant="outlined" startIcon={<DownloadIcon />} onClick={() => setExportOpen(true)}>
            Export
          </Button>
          <Button variant="outlined" startIcon={<ShareIcon />} onClick={() => setExportOpen(true)}>
            Share
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Box>
                  <Typography variant="overline" color="text.secondary">Bill From</Typography>
                  {invoice.issuer_name && <Typography fontWeight={700} color="primary.main">{invoice.issuer_name}</Typography>}
                  {invoice.issuer_email && <Typography variant="body2" color="text.secondary">{invoice.issuer_email}</Typography>}
                  {invoice.issuer_phone && <Typography variant="body2" color="text.secondary">{invoice.issuer_phone}</Typography>}
                  {invoice.issuer_address && <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: "pre-line" }}>{invoice.issuer_address}</Typography>}
                </Box>
                <Box sx={{ textAlign: "right" }}>
                  <Typography variant="overline" color="text.secondary">Bill To</Typography>
                  <Typography fontWeight={700} color="primary.main">{invoice.customer_name}</Typography>
                  {invoice.customer_email && <Typography variant="body2" color="text.secondary">{invoice.customer_email}</Typography>}
                </Box>
              </Box>

              <Box sx={{ display: "flex", gap: 3, py: 2, borderTop: "1px solid", borderBottom: "1px solid", borderColor: "divider", mb: 3 }}>
                {[
                  { label: "Issue Date", value: dayjs(invoice.issue_date).format("MMM D, YYYY") },
                  { label: "Due Date", value: dayjs(invoice.due_date).format("MMM D, YYYY") },
                  { label: "Currency", value: invoice.currency },
                ].map((m) => (
                  <Box key={m.label}>
                    <Typography variant="caption" color="text.secondary" sx={{ letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 700 }}>
                      {m.label}
                    </Typography>
                    <Typography fontWeight={500}>{m.value}</Typography>
                  </Box>
                ))}
              </Box>

              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Qty</TableCell>
                      <TableCell align="right">Unit Price</TableCell>
                      <TableCell align="right">Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {invoice.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell sx={{ fontWeight: 600 }}>{item.description}</TableCell>
                        <TableCell align="right">{item.quantity}</TableCell>
                        <TableCell align="right">{invoice.currency} {Number(item.unit_price).toFixed(2)}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600 }}>{invoice.currency} {Number(item.line_total).toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {payments && payments.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h5" sx={{ mb: 2 }}>Payments</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Method</TableCell>
                        <TableCell>Reference</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {payments.map((p: any) => (
                        <TableRow key={p.id}>
                          <TableCell>{dayjs(p.payment_date).format("MMM D, YYYY")}</TableCell>
                          <TableCell>{p.payment_method}</TableCell>
                          <TableCell>{p.reference_number || "—"}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600, color: "success.main" }}>
                            {invoice.currency} {Number(p.amount).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}

          {history && history.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h5" sx={{ mb: 2 }}>Status History</Typography>
                <List disablePadding>
                  {history.map((h) => (
                    <ListItem key={h.id} sx={{ px: 0 }}>
                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight={600} sx={{ textTransform: "capitalize" }}>
                            {h.status}
                          </Typography>
                        }
                        secondary={
                          <>
                            <Typography variant="caption" color="text.secondary">
                              {dayjs(h.created_at).format("MMM D, YYYY h:mm A")}
                            </Typography>
                            {h.notes && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                {h.notes}
                              </Typography>
                            )}
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 2 }}>Summary</Typography>
              {[
                { label: "Subtotal", value: invoice.subtotal },
                { label: `Tax (${invoice.tax_rate}%)`, value: invoice.tax_amount },
              ].map((row) => (
                <Box key={row.label} sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">{row.label}</Typography>
                  <Typography variant="body2" sx={{ fontFeatureSettings: '"tnum"' }}>
                    {invoice.currency} {Number(row.value).toFixed(2)}
                  </Typography>
                </Box>
              ))}
              <Divider sx={{ my: 1.5 }} />
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <Typography fontWeight={700}>Total</Typography>
                <Typography variant="h3" color="primary.main" fontWeight={700}>
                  {invoice.currency} {Number(invoice.total_amount).toFixed(2)}
                </Typography>
              </Box>
              {invoice.paid_amount > 0 && (
                <Box sx={{ display: "flex", justifyContent: "space-between", mt: 1 }}>
                  <Typography variant="body2" color="success.main" fontWeight={600}>Paid</Typography>
                  <Typography variant="body2" color="success.main" fontWeight={600}>
                    {invoice.currency} {Number(invoice.paid_amount).toFixed(2)}
                  </Typography>
                </Box>
              )}
              {outstanding > 0 && (
                <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
                  <Typography variant="body2" color="warning.main" fontWeight={600}>Outstanding</Typography>
                  <Typography variant="body2" color="warning.main" fontWeight={600}>
                    {invoice.currency} {outstanding.toFixed(2)}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {invoice.payment_bank_name && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h5" sx={{ mb: 1.5 }}>Payment Details</Typography>
                <Typography fontWeight={700}>{invoice.payment_bank_name}</Typography>
                {invoice.payment_account_number && <Typography variant="body2" color="text.secondary">{invoice.payment_account_number}</Typography>}
                {invoice.payment_account_name && <Typography variant="body2" color="text.secondary">{invoice.payment_account_name}</Typography>}
              </CardContent>
            </Card>
          )}

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                <Typography variant="h5">Logo</Typography>
                <label htmlFor="logo-upload">
                  <IconButton component="span" size="small">
                    <UploadFileIcon fontSize="small" />
                  </IconButton>
                </label>
                <input id="logo-upload" type="file" accept="image/*" hidden onChange={handleLogoUpload} />
              </Box>
              {invoice.logo_path ? (
                <Box
                  component="img"
                  src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/media/${invoice.logo_path}`}
                  alt="Invoice logo"
                  sx={{ maxWidth: "100%", maxHeight: 80, objectFit: "contain" }}
                />
              ) : (
                <Box sx={{ width: 48, height: 48, borderRadius: 1, bgcolor: "primary.main", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 20 }}>
                  #
                </Box>
              )}
            </CardContent>
          </Card>

          {invoice.notes && (
            <Card>
              <CardContent>
                <Typography variant="h5" sx={{ mb: 1 }}>Notes</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: "pre-line" }}>
                  {invoice.notes}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      <ExportDialog open={exportOpen} onClose={() => setExportOpen(false)} invoiceId={id} invoiceNumber={invoice.invoice_number} />

      <Dialog open={paymentOpen} onClose={() => setPaymentOpen(false)}>
        <DialogTitle>Record Payment</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1, minWidth: 350 }}>
            <TextField label="Amount" type="number" value={paymentForm.amount} onChange={(e) => setPaymentForm((p) => ({ ...p, amount: e.target.value }))} fullWidth required />
            <TextField label="Payment Method" select value={paymentForm.payment_method} onChange={(e) => setPaymentForm((p) => ({ ...p, payment_method: e.target.value }))} fullWidth>
              {["bank_transfer", "cash", "check", "credit_card", "mobile_money", "other"].map((m) => (
                <option key={m} value={m}>{m.replace("_", " ")}</option>
              ))}
            </TextField>
            <TextField label="Reference Number" value={paymentForm.reference_number} onChange={(e) => setPaymentForm((p) => ({ ...p, reference_number: e.target.value }))} fullWidth />
            <TextField label="Notes" value={paymentForm.notes} onChange={(e) => setPaymentForm((p) => ({ ...p, notes: e.target.value }))} fullWidth multiline rows={2} />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleRecordPayment} disabled={createPayment.isPending || !paymentForm.amount}>
            Record
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
