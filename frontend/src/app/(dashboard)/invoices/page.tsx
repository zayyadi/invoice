"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Box, Chip, Stack } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { useInvoices } from "@/lib/queries";
import PageHeader from "@/components/common/PageHeader";
import SearchInput from "@/components/common/SearchInput";
import InvoiceTable from "@/components/invoices/InvoiceTable";
import EmptyState from "@/components/common/EmptyState";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";

const STATUSES = ["", "draft", "sent", "viewed", "partial", "paid", "overdue", "cancelled"];

export default function InvoicesPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const { data: invoices, isLoading } = useInvoices({ status: statusFilter || undefined, search: search || undefined });

  return (
    <Box>
      <PageHeader
        title="Invoices"
        subtitle={`${invoices?.length || 0} total invoices`}
        action={{ label: "Create Invoice", icon: <AddIcon />, onClick: () => router.push("/invoices/new") }}
      />

      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: { xs: "stretch", md: "center" }, mb: 3, gap: 2, flexDirection: { xs: "column", md: "row" } }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search invoices..." />
        <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
          {STATUSES.filter(Boolean).map((s) => (
            <Chip
              key={s}
              label={s.charAt(0).toUpperCase() + s.slice(1)}
              onClick={() => setStatusFilter(statusFilter === s ? "" : s)}
              variant={statusFilter === s ? "filled" : "outlined"}
              color={statusFilter === s ? "primary" : "default"}
              size="small"
            />
          ))}
        </Stack>
      </Box>

      {isLoading ? (
        <TableSkeleton rows={8} cols={8} />
      ) : invoices && invoices.length > 0 ? (
        <InvoiceTable invoices={invoices} />
      ) : (
        <EmptyState
          icon={<ReceiptLongIcon />}
          title="No invoices yet"
          description="Create your first invoice to get started"
          action={{ label: "Create Invoice", onClick: () => router.push("/invoices/new") }}
        />
      )}
    </Box>
  );
}
