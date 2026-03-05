"use client";

import { Button, Stack } from "@mui/material";

import { exportInvoice } from "@/lib/api";

type Props = {
  invoiceId: string;
};

export default function ExportButtons({ invoiceId }: Props) {
  return (
    <Stack direction="row" spacing={2}>
      <Button variant="contained" onClick={() => exportInvoice(invoiceId, "pdf")}>
        Export PDF
      </Button>
      <Button variant="outlined" onClick={() => exportInvoice(invoiceId, "png")}>
        Export PNG
      </Button>
      <Button variant="outlined" onClick={() => exportInvoice(invoiceId, "jpg")}>
        Export JPG
      </Button>
    </Stack>
  );
}
