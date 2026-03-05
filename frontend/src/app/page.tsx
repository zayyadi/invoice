import Link from "next/link";
import { Button, Container, Stack, Typography } from "@mui/material";

export default function HomePage() {
  return (
    <Container sx={{ py: 8 }}>
      <Stack spacing={2}>
        <Typography variant="h4">Invoice Generator</Typography>
        <Typography>Create invoices in Naira and export as PDF/PNG/JPG.</Typography>
        <Button component={Link} href="/invoices/new" variant="contained" sx={{ width: "fit-content" }}>
          Create New Invoice
        </Button>
      </Stack>
    </Container>
  );
}
