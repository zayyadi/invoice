"use client";

import { Box, Typography } from "@mui/material";
import { useParams } from "next/navigation";
import ClientForm from "@/components/clients/ClientForm";

export default function EditClientPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <Box>
      <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
        Edit Client
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Update client details and billing preferences
      </Typography>
      <ClientForm clientId={id} />
    </Box>
  );
}
