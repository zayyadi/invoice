"use client";

import Link from "next/link";
import { useState } from "react";
import { Alert, Button, Container, Grid, Stack, Typography } from "@mui/material";

import ExportButtons from "@/components/ExportButtons";
import InvoiceForm from "@/components/InvoiceForm";
import InvoicePreview from "@/components/InvoicePreview";
import LogoUploader from "@/components/LogoUploader";
import { getInvoice } from "@/lib/api";
import { Invoice } from "@/lib/types";

export default function NewInvoicePage() {
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [error, setError] = useState<string>("");

  async function refreshInvoice() {
    if (!invoice) return;
    const latest = await getInvoice(invoice.id);
    setInvoice(latest);
  }

  return (
    <Container sx={{ py: 4 }}>
      <Stack spacing={3}>
        <Typography variant="h4">New Invoice</Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <InvoiceForm
              onCreated={(created) => {
                setError("");
                setInvoice(created);
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 6 }}>
            {invoice ? (
              <Stack spacing={2}>
                <Stack direction="row" spacing={2}>
                  <LogoUploader
                    invoiceId={invoice.id}
                    onUploaded={async () => {
                      try {
                        await refreshInvoice();
                      } catch {
                        setError("Logo upload succeeded but refresh failed");
                      }
                    }}
                  />
                  <Button component={Link} href={`/invoices/${invoice.id}`} variant="text">
                    Open Invoice Page
                  </Button>
                </Stack>

                <ExportButtons invoiceId={invoice.id} />
                <InvoicePreview invoice={invoice} />
              </Stack>
            ) : (
              <Alert severity="info">Create an invoice to see preview and export options.</Alert>
            )}
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
}
