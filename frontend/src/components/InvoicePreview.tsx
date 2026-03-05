import { Card, CardContent, Divider, Stack, Typography } from "@mui/material";

import { API_URL } from "@/lib/api";
import { Invoice } from "@/lib/types";

type Props = {
  invoice: Invoice;
};

function naira(value: string | number) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value));
}

export default function InvoicePreview({ invoice }: Props) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
            <Stack sx={{ minWidth: 0, flex: 1 }}>
              <Typography variant="h5" sx={{ wordBreak: "break-word" }}>
                Invoice #{invoice.invoice_number}
              </Typography>
              <Typography sx={{ wordBreak: "break-word" }}>Bill To: {invoice.customer_name}</Typography>
              {invoice.customer_email ? (
                <Typography sx={{ wordBreak: "break-word" }}>Bill To Email: {invoice.customer_email}</Typography>
              ) : null}
              <Typography sx={{ wordBreak: "break-word" }}>Issue: {invoice.issue_date}</Typography>
              <Typography sx={{ wordBreak: "break-word" }}>Due: {invoice.due_date}</Typography>
            </Stack>
            {invoice.logo_path ? (
              <img
                src={`${API_URL}${invoice.logo_path}`}
                alt="Company logo"
                style={{ maxHeight: 72, maxWidth: 180, objectFit: "contain" }}
              />
            ) : null}
          </Stack>

          <Divider sx={{ my: 1 }} />

          {invoice.items.map((item) => (
            <Stack key={item.id} direction="row" justifyContent="space-between">
              <Typography>
                {item.description} ({item.quantity} x {naira(item.unit_price)})
              </Typography>
              <Typography>{naira(item.line_total)}</Typography>
            </Stack>
          ))}

          <Divider sx={{ my: 1 }} />

          <Stack direction="row" justifyContent="space-between">
            <Typography>Subtotal</Typography>
            <Typography>{naira(invoice.subtotal)}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography>Tax</Typography>
            <Typography>{naira(invoice.tax_amount)}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="h6">Total</Typography>
            <Typography variant="h6">{naira(invoice.total_amount)}</Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
