"use client";

import { useEffect, useState } from "react";
import { Alert, Container, Stack, Typography } from "@mui/material";

import ExportButtons from "@/components/ExportButtons";
import InvoicePreview from "@/components/InvoicePreview";
import LogoUploader from "@/components/LogoUploader";
import { getInvoice } from "@/lib/api";
import { Invoice } from "@/lib/types";

type Params = {
  params: { id: string };
};

export default function InvoicePage({ params }: Params) {
  const invoiceId = params.id;
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!invoiceId) return;
    getInvoice(invoiceId)
      .then(setInvoice)
      .catch(() => setError("Failed to load invoice"));
  }, [invoiceId]);

  return (
    <Container sx={{ py: 4 }}>
      <Stack spacing={2}>
        <Typography variant="h4">Invoice Details</Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}

        {invoice ? (
          <>
            <LogoUploader
              invoiceId={invoice.id}
              onUploaded={async () => {
                const latest = await getInvoice(invoice.id);
                setInvoice(latest);
              }}
            />
            <ExportButtons invoiceId={invoice.id} />
            <InvoicePreview invoice={invoice} />
          </>
        ) : (
          <Alert severity="info">Loading invoice...</Alert>
        )}
      </Stack>
    </Container>
  );
}
