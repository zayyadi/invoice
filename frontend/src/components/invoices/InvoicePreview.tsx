"use client";

import { Box, Typography, Paper } from "@mui/material";

interface PreviewItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

interface Props {
  data: {
    invoice_number: string;
    customer_name: string;
    customer_email?: string;
    issuer_name?: string;
    issuer_email?: string;
    issuer_phone?: string;
    issuer_address?: string;
    payment_bank_name?: string;
    payment_account_number?: string;
    payment_account_name?: string;
    issue_date: string;
    due_date: string;
    currency: string;
    items: PreviewItem[];
    subtotal: number;
    tax_amount: number;
    total_amount: number;
    notes?: string;
    status: string;
    logo_path: string | null;
  };
}

export default function InvoicePreview({ data }: Props) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
        bgcolor: "#ffffff",
        fontSize: 12,
        lineHeight: 1.4,
        transform: "scale(0.85)",
        transformOrigin: "top left",
        width: "117%",
      }}
    >
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Box>
          <Box
            sx={{
              display: "inline-block",
              px: 1,
              py: 0.25,
              borderRadius: 0.5,
              bgcolor: "error.light",
              color: "error.dark",
              fontSize: 9,
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              mb: 1,
            }}
          >
            {data.status}
          </Box>
          <Typography variant="caption" sx={{ display: "block", color: "text.secondary", letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 700, fontSize: 9 }}>
            Invoice Number
          </Typography>
          <Typography sx={{ color: "primary.main", fontWeight: 700, fontSize: 20, lineHeight: 1.1 }}>
            #{data.invoice_number}
          </Typography>
        </Box>
        <Box sx={{ width: 36, height: 36, borderRadius: 1, bgcolor: "primary.main", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 16 }}>
          A
        </Box>
      </Box>

      <Box sx={{ display: "flex", gap: 2, py: 1.5, borderTop: "1px solid", borderBottom: "1px solid", borderColor: "divider", mb: 2 }}>
        {[
          { label: "Issued", value: data.issue_date },
          { label: "Due", value: data.due_date },
          { label: "Currency", value: data.currency },
          { label: "Lines", value: String(data.items.length) },
        ].map((m) => (
          <Box key={m.label} sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
              {m.label}
            </Typography>
            <Typography sx={{ fontWeight: 500, fontSize: 12 }}>{m.value}</Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        {data.issuer_name && (
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
              Bill From
            </Typography>
            <Typography sx={{ fontWeight: 700, color: "primary.main", fontSize: 12 }}>{data.issuer_name}</Typography>
            {data.issuer_email && <Typography sx={{ color: "text.secondary", fontSize: 11 }}>{data.issuer_email}</Typography>}
            {data.issuer_phone && <Typography sx={{ color: "text.secondary", fontSize: 11 }}>{data.issuer_phone}</Typography>}
          </Box>
        )}
        <Box sx={{ flex: 1 }}>
          <Typography variant="caption" sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
            Bill To
          </Typography>
          <Typography sx={{ fontWeight: 700, color: "primary.main", fontSize: 12 }}>{data.customer_name || "—"}</Typography>
          {data.customer_email && <Typography sx={{ color: "text.secondary", fontSize: 11 }}>{data.customer_email}</Typography>}
        </Box>
      </Box>

      <Box component="table" sx={{ width: "100%", borderCollapse: "collapse", mb: 2 }}>
        <Box component="thead">
          <Box component="tr">
            {["Description", "Qty", "Unit", "Total"].map((h) => (
              <Box
                component="th"
                key={h}
                sx={{
                  px: 1,
                  py: 1,
                  bgcolor: "surface-high",
                  color: "text.secondary",
                  fontSize: 9,
                  fontWeight: 700,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  textAlign: h === "Total" ? "right" : "left",
                  borderBottom: "1px solid",
                  borderColor: "divider",
                }}
              >
                {h}
              </Box>
            ))}
          </Box>
        </Box>
        <Box component="tbody">
          {data.items.map((item) => (
            <Box component="tr" key={item.id}>
              <Box component="td" sx={{ px: 1, py: 1, borderBottom: "1px solid #e7cfd1", fontWeight: 600, fontSize: 11 }}>
                {item.description}
              </Box>
              <Box component="td" sx={{ px: 1, py: 1, borderBottom: "1px solid #e7cfd1", color: "text.secondary", fontWeight: 500, fontSize: 11 }}>
                {item.quantity}
              </Box>
              <Box component="td" sx={{ px: 1, py: 1, borderBottom: "1px solid #e7cfd1", color: "text.secondary", fontSize: 11 }}>
                {data.currency} {item.unit_price.toFixed(2)}
              </Box>
              <Box component="td" sx={{ px: 1, py: 1, borderBottom: "1px solid #e7cfd1", textAlign: "right", fontWeight: 600, color: "primary.main", fontSize: 11 }}>
                {data.currency} {item.line_total.toFixed(2)}
              </Box>
            </Box>
          ))}
        </Box>
      </Box>

      <Box sx={{ display: "flex", gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          {data.payment_bank_name && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="caption" sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                Payment Details
              </Typography>
              <Box sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1, mt: 0.5 }}>
                <Typography sx={{ fontWeight: 700, fontSize: 11 }}>{data.payment_bank_name}</Typography>
                {data.payment_account_number && <Typography sx={{ color: "text.secondary", fontSize: 10 }}>{data.payment_account_number}</Typography>}
                {data.payment_account_name && <Typography sx={{ color: "text.secondary", fontSize: 10 }}>{data.payment_account_name}</Typography>}
              </Box>
            </Box>
          )}
          {data.notes && (
            <Box sx={{ p: 1, border: "1px solid rgba(54,100,92,0.35)", borderRadius: 1, bgcolor: "rgba(160,208,198,0.08)" }}>
              <Typography variant="caption" sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                Notes
              </Typography>
              <Typography sx={{ color: "#204e47", fontSize: 10, mt: 0.25 }}>{data.notes}</Typography>
            </Box>
          )}
        </Box>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ p: 1.5, border: "1px solid", borderColor: "divider", borderRadius: 1, bgcolor: "#fff0f0" }}>
            {[
              { label: "Subtotal", value: data.subtotal },
              { label: "Tax", value: data.tax_amount },
            ].map((row) => (
              <Box key={row.label} sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
                <Typography sx={{ color: "text.secondary", fontSize: 11 }}>{row.label}</Typography>
                <Typography sx={{ fontWeight: 500, fontSize: 11 }}>{data.currency} {row.value.toFixed(2)}</Typography>
              </Box>
            ))}
            <Box sx={{ height: 1, bgcolor: "divider", my: 1 }} />
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
              <Typography sx={{ color: "text.secondary", fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                Total
              </Typography>
              <Typography sx={{ color: "primary.main", fontWeight: 700, fontSize: 18, lineHeight: 1 }}>
                {data.currency} {data.total_amount.toFixed(2)}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}
