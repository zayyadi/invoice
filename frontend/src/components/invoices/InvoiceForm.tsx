"use client";

import { useState } from "react";
import {
  Box, TextField, Typography, Button, Divider, Grid,
  MenuItem, Autocomplete, Card, CardContent, Alert,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import SaveIcon from "@mui/icons-material/Save";
import dayjs from "dayjs";
import { useCreateInvoice, useClients } from "@/lib/queries";
import type { InvoiceCreate } from "@/lib/types";
import LineItemRow from "./LineItemRow";
import InvoicePreview from "./InvoicePreview";
import { useRouter } from "next/navigation";

export interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
}

const EMPTY_ITEM: LineItem = { description: "", quantity: 1, unit_price: 0 };

const CURRENCIES = ["NGN", "USD", "GBP", "EUR"];

export default function InvoiceForm() {
  const router = useRouter();
  const createInvoice = useCreateInvoice();
  const { data: clients } = useClients();

  const [form, setForm] = useState({
    invoice_number: "",
    customer_name: "",
    customer_email: "",
    issuer_name: "",
    issuer_email: "",
    issuer_phone: "",
    issuer_address: "",
    payment_bank_name: "",
    payment_account_number: "",
    payment_account_name: "",
    issue_date: dayjs().format("YYYY-MM-DD"),
    due_date: dayjs().add(30, "day").format("YYYY-MM-DD"),
    currency: "NGN",
    tax_rate: 0,
    notes: "",
    client_id: null as string | null,
  });

  const [items, setItems] = useState<LineItem[]>([{ ...EMPTY_ITEM }]);
  const [error, setError] = useState<string | null>(null);

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const taxAmount = subtotal * (form.tax_rate / 100);
  const total = subtotal + taxAmount;

  const updateField = (field: string, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateItem = (index: number, field: keyof LineItem, value: string | number) => {
    setItems((prev) => prev.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  };

  const addItem = () => setItems((prev) => [...prev, { ...EMPTY_ITEM }]);
  const removeItem = (index: number) => setItems((prev) => prev.filter((_, i) => i !== index));

  const handleClientSelect = (_: any, client: any) => {
    if (client) {
      setForm((prev) => ({
        ...prev,
        client_id: client.id,
        customer_name: client.name,
        customer_email: client.email || "",
      }));
    } else {
      setForm((prev) => ({ ...prev, client_id: null, customer_name: "", customer_email: "" }));
    }
  };

  const handleSubmit = async () => {
    if (!form.invoice_number.trim()) { setError("Invoice number is required"); return; }
    if (!form.customer_name.trim()) { setError("Customer name is required"); return; }
    if (items.length === 0 || items.every((i) => !i.description.trim())) { setError("Add at least one line item"); return; }

    try {
      const payload: InvoiceCreate = {
        invoice_number: form.invoice_number,
        customer_name: form.customer_name,
        customer_email: form.customer_email || undefined,
        issuer_name: form.issuer_name || undefined,
        issuer_email: form.issuer_email || undefined,
        issuer_phone: form.issuer_phone || undefined,
        issuer_address: form.issuer_address || undefined,
        payment_bank_name: form.payment_bank_name || undefined,
        payment_account_number: form.payment_account_number || undefined,
        payment_account_name: form.payment_account_name || undefined,
        issue_date: form.issue_date,
        due_date: form.due_date,
        currency: form.currency,
        tax_rate: form.tax_rate,
        notes: form.notes || undefined,
        client_id: form.client_id || undefined,
        items: items.filter((i) => i.description.trim()).map((i) => ({
          description: i.description,
          quantity: i.quantity,
          unit_price: i.unit_price,
        })),
      };
      const invoice = await createInvoice.mutateAsync(payload);
      router.push(`/invoices/${invoice.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create invoice");
    }
  };

  const previewData = {
    ...form,
    items: items.filter((i) => i.description.trim()).map((item, idx) => ({
      id: idx + 1,
      description: item.description,
      quantity: item.quantity,
      unit_price: item.unit_price,
      line_total: item.quantity * item.unit_price,
    })),
    subtotal,
    tax_amount: taxAmount,
    total_amount: total,
    status: "draft" as const,
    logo_path: null,
  };

  return (
    <Box sx={{ display: "flex", gap: 4, alignItems: "flex-start", flexDirection: { xs: "column", lg: "row" } }}>
      <Box sx={{ flex: 5, width: "100%", minWidth: 0 }}>
        <Card>
          <CardContent sx={{ p: 4 }}>
            {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</Alert>}

            <Typography variant="subtitle1" sx={{ mb: 2, color: "text.secondary" }}>
              Invoice Details
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <TextField label="Invoice Number" fullWidth required value={form.invoice_number} onChange={(e) => updateField("invoice_number", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Autocomplete
                  options={clients || []}
                  getOptionLabel={(opt) => opt.name}
                  onChange={handleClientSelect}
                  renderInput={(params) => <TextField {...params} label="Select Client (optional)" />}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Customer Name" fullWidth required value={form.customer_name} onChange={(e) => updateField("customer_name", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Customer Email" fullWidth value={form.customer_email} onChange={(e) => updateField("customer_email", e.target.value)} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField label="Issue Date" type="date" fullWidth value={form.issue_date} onChange={(e) => updateField("issue_date", e.target.value)} InputLabelProps={{ shrink: true }} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField label="Due Date" type="date" fullWidth value={form.due_date} onChange={(e) => updateField("due_date", e.target.value)} InputLabelProps={{ shrink: true }} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField label="Currency" select fullWidth value={form.currency} onChange={(e) => updateField("currency", e.target.value)}>
                  {CURRENCIES.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                </TextField>
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField label="Tax Rate %" type="number" fullWidth value={form.tax_rate} onChange={(e) => updateField("tax_rate", parseFloat(e.target.value) || 0)} inputProps={{ min: 0, max: 100, step: 0.5 }} />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" sx={{ mb: 2, color: "text.secondary" }}>
              Bill From (Issuer)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <TextField label="Issuer Name" fullWidth value={form.issuer_name} onChange={(e) => updateField("issuer_name", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Issuer Email" fullWidth value={form.issuer_email} onChange={(e) => updateField("issuer_email", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Issuer Phone" fullWidth value={form.issuer_phone} onChange={(e) => updateField("issuer_phone", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Issuer Address" fullWidth multiline rows={2} value={form.issuer_address} onChange={(e) => updateField("issuer_address", e.target.value)} />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" sx={{ mb: 2, color: "text.secondary" }}>
              Payment Details
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <TextField label="Bank Name" fullWidth value={form.payment_bank_name} onChange={(e) => updateField("payment_bank_name", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField label="Account Number" fullWidth value={form.payment_account_number} onChange={(e) => updateField("payment_account_number", e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField label="Account Name" fullWidth value={form.payment_account_name} onChange={(e) => updateField("payment_account_name", e.target.value)} />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" sx={{ mb: 2, color: "text.secondary" }}>
              Line Items
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: "flex", gap: 1.5, mb: 1, px: 0.5 }}>
                <Typography variant="caption" sx={{ flex: 3 }}>Description</Typography>
                <Typography variant="caption" sx={{ flex: 0.8 }}>Qty</Typography>
                <Typography variant="caption" sx={{ flex: 1.2 }}>Unit Price</Typography>
                <Typography variant="caption" sx={{ flex: 1.2 }}>Total</Typography>
                <Box sx={{ width: 40 }} />
              </Box>
              {items.map((item, i) => (
                <LineItemRow key={i} item={item} index={i} currency={form.currency} onChange={updateItem} onRemove={removeItem} canRemove={items.length > 1} />
              ))}
              <Button startIcon={<AddIcon />} onClick={addItem} size="small" sx={{ mt: 1 }}>
                Add item
              </Button>
            </Box>

            <Divider sx={{ my: 3 }} />

            <TextField label="Notes & Terms" fullWidth multiline rows={3} value={form.notes} onChange={(e) => updateField("notes", e.target.value)} sx={{ mb: 3 }} />

            <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
              <Button variant="outlined" onClick={() => router.back()}>
                Cancel
              </Button>
              <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSubmit} disabled={createInvoice.isPending}>
                {createInvoice.isPending ? "Creating..." : "Create Invoice"}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      <Box sx={{ flex: 2, position: { xs: "static", lg: "sticky" }, top: 80, width: "100%", minWidth: 0 }}>
        <Typography variant="overline" sx={{ mb: 1.5, display: "block", color: "text.secondary" }}>
          Live Preview
        </Typography>
        <InvoicePreview data={previewData} />
      </Box>
    </Box>
  );
}
