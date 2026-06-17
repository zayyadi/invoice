"use client";

import { Chip } from "@mui/material";
import type { InvoiceStatus } from "@/lib/types";

const CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  draft: { label: "Draft", color: "#564244", bg: "rgba(137,113,115,0.12)" },
  sent: { label: "Sent", color: "#a1354c", bg: "rgba(161,53,76,0.12)" },
  viewed: { label: "Viewed", color: "#0277bd", bg: "rgba(2,119,189,0.12)" },
  partial: { label: "Partial", color: "#e6a817", bg: "rgba(230,168,23,0.12)" },
  paid: { label: "Paid", color: "#36645c", bg: "rgba(54,100,92,0.12)" },
  overdue: { label: "Overdue", color: "#ba1a1a", bg: "rgba(186,26,26,0.12)" },
  cancelled: { label: "Cancelled", color: "#897173", bg: "rgba(137,113,115,0.12)" },
};

export default function StatusChip({ status }: { status: InvoiceStatus }) {
  const cfg = CONFIG[status] || CONFIG.draft;
  return (
    <Chip
      label={cfg.label}
      size="small"
      sx={{
        backgroundColor: cfg.bg,
        color: cfg.color,
        fontWeight: 600,
        fontSize: 12,
        textTransform: "capitalize",
        height: 26,
      }}
    />
  );
}
