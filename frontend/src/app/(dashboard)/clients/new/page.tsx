"use client";

import { Box, Typography } from "@mui/material";
import ClientForm from "@/components/clients/ClientForm";

export default function NewClientPage() {
  return (
    <Box>
      <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
        Add Client
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Add a new client to your directory
      </Typography>
      <ClientForm />
    </Box>
  );
}
