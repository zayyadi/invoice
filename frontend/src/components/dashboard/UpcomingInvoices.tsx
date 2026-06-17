"use client";

import { Card, CardContent, Typography, List, ListItem, ListItemText, Chip, Box } from "@mui/material";
import type { UpcomingInvoice } from "@/lib/types";
import dayjs from "dayjs";

interface Props {
  invoices: UpcomingInvoice[];
}

export default function UpcomingInvoices({ invoices }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Upcoming
        </Typography>
        {invoices.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No upcoming invoices
          </Typography>
        ) : (
          <List disablePadding>
            {invoices.map((inv) => (
              <ListItem key={inv.id} sx={{ px: 0, py: 1 }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <Typography variant="body2" fontWeight={600}>
                        {inv.invoice_number}
                      </Typography>
                      <Typography variant="body2" fontWeight={600} sx={{ fontFeatureSettings: '"tnum"' }}>
                        {inv.currency} {inv.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {inv.customer_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Due {dayjs(inv.due_date).format("MMM D")} ({inv.days_until_due}d)
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
