"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Box } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PeopleIcon from "@mui/icons-material/People";
import { useClients } from "@/lib/queries";
import PageHeader from "@/components/common/PageHeader";
import SearchInput from "@/components/common/SearchInput";
import ClientTable from "@/components/clients/ClientTable";
import EmptyState from "@/components/common/EmptyState";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";

export default function ClientsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const { data: clients, isLoading } = useClients(search || undefined);

  return (
    <Box>
      <PageHeader
        title="Clients"
        subtitle={`${clients?.length || 0} total clients`}
        action={{ label: "Add Client", icon: <AddIcon />, onClick: () => router.push("/clients/new") }}
      />

      <Box sx={{ mb: 3 }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search clients..." />
      </Box>

      {isLoading ? (
        <TableSkeleton rows={6} cols={7} />
      ) : clients && clients.length > 0 ? (
        <ClientTable clients={clients} />
      ) : (
        <EmptyState
          icon={<PeopleIcon />}
          title="No clients yet"
          description="Add your first client to start creating invoices for them"
          action={{ label: "Add Client", onClick: () => router.push("/clients/new") }}
        />
      )}
    </Box>
  );
}
