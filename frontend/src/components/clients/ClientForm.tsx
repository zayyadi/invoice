"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, Grid, TextField, Button, Typography, Alert, MenuItem, Box } from "@mui/material";
import { useCreateClient, useUpdateClient, useClient } from "@/lib/queries";
import type { ClientCreate, ClientUpdate } from "@/lib/types";

const CURRENCIES = ["NGN", "USD", "GBP", "EUR"];

export default function ClientForm({ clientId }: { clientId?: string }) {
  const router = useRouter();
  const { data: existing } = useClient(clientId || "");
  const createClient = useCreateClient();
  const updateClient = useUpdateClient(clientId || "");

  const [form, setForm] = useState<ClientCreate & { name: string }>({
    name: "",
    email: "",
    phone: "",
    address: "",
    tax_id: "",
    notes: "",
    default_currency: "NGN",
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (existing) {
      setForm({
        name: existing.name,
        email: existing.email || "",
        phone: existing.phone || "",
        address: existing.address || "",
        tax_id: existing.tax_id || "",
        notes: existing.notes || "",
        default_currency: existing.default_currency || "NGN",
      });
    }
  }, [existing]);

  const updateField = (field: string, value: string | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!form.name.trim()) { setError("Name is required"); return; }
    try {
      if (clientId) {
        await updateClient.mutateAsync(form as ClientUpdate);
        router.push(`/clients/${clientId}`);
      } else {
        const client = await createClient.mutateAsync(form);
        router.push(`/clients/${client.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to save client");
    }
  };

  const isLoading = createClient.isPending || updateClient.isPending;

  return (
    <Card>
      <CardContent sx={{ p: 4 }}>
        {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</Alert>}

        <Grid container spacing={2.5}>
          <Grid item xs={12} sm={6}>
            <TextField label="Name" fullWidth required value={form.name} onChange={(e) => updateField("name", e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField label="Email" fullWidth value={form.email} onChange={(e) => updateField("email", e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField label="Phone" fullWidth value={form.phone} onChange={(e) => updateField("phone", e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField label="Tax ID" fullWidth value={form.tax_id} onChange={(e) => updateField("tax_id", e.target.value)} />
          </Grid>
          <Grid item xs={12}>
            <TextField label="Address" fullWidth multiline rows={2} value={form.address} onChange={(e) => updateField("address", e.target.value)} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField label="Default Currency" select fullWidth value={form.default_currency} onChange={(e) => updateField("default_currency", e.target.value)}>
              {CURRENCIES.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <TextField label="Notes" fullWidth multiline rows={3} value={form.notes} onChange={(e) => updateField("notes", e.target.value)} />
          </Grid>
        </Grid>

        <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end", mt: 4 }}>
          <Button variant="outlined" onClick={() => router.back()}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? "Saving..." : clientId ? "Update Client" : "Create Client"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}
