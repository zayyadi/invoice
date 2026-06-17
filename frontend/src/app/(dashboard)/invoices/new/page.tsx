"use client";

import { Box, Typography } from "@mui/material";
import InvoiceForm from "@/components/invoices/InvoiceForm";

export default function NewInvoicePage() {
  return (
    <Box>
      <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
        Create Invoice
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Fill in the details below to create a new invoice
      </Typography>
      <InvoiceForm />
    </Box>
  );
}
