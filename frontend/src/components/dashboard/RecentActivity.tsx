"use client";

import { Card, CardContent, Typography, List, ListItem, ListItemText, ListItemIcon, Box, Chip } from "@mui/material";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import PaymentsIcon from "@mui/icons-material/Payments";
import type { Activity } from "@/lib/types";
import dayjs from "dayjs";

interface Props {
  activities: Activity[];
}

export default function RecentActivity({ activities }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Recent Activity
        </Typography>
        {activities.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No recent activity
          </Typography>
        ) : (
          <List disablePadding>
            {activities.map((a) => (
              <ListItem key={a.id} sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  {a.type === "payment_received" ? (
                    <PaymentsIcon fontSize="small" sx={{ color: "success.main" }} />
                  ) : (
                    <ReceiptLongIcon fontSize="small" sx={{ color: "primary.main" }} />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <Typography variant="body2" fontWeight={500}>
                        {a.description}
                      </Typography>
                      <Typography variant="body2" fontWeight={600} sx={{ fontFeatureSettings: '"tnum"' }}>
                        NGN {a.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {dayjs(a.timestamp).format("MMM D, YYYY")}
                    </Typography>
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
