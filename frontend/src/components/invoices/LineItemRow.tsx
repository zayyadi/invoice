"use client";

import { Box, IconButton, TextField, Typography } from "@mui/material";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import type { LineItem } from "./InvoiceForm";

interface Props {
  item: LineItem;
  index: number;
  currency: string;
  onChange: (index: number, field: keyof LineItem, value: string | number) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
}

export default function LineItemRow({ item, index, currency, onChange, onRemove, canRemove }: Props) {
  const lineTotal = item.quantity * item.unit_price;

  return (
    <Box sx={{ display: "flex", gap: 1.5, alignItems: "flex-start", mb: 1.5, flexWrap: { xs: "wrap", sm: "nowrap" } }}>
      <TextField
        placeholder="Description"
        value={item.description}
        onChange={(e) => onChange(index, "description", e.target.value)}
        sx={{ flex: { xs: "1 1 100%", sm: 3 } }}
        size="small"
      />
      <TextField
        type="number"
        placeholder="Qty"
        value={item.quantity || ""}
        onChange={(e) => onChange(index, "quantity", parseInt(e.target.value) || 0)}
        sx={{ flex: { xs: "1 1 80px", sm: 0.8 } }}
        size="small"
        inputProps={{ min: 0 }}
      />
      <TextField
        type="number"
        placeholder="Unit Price"
        value={item.unit_price || ""}
        onChange={(e) => onChange(index, "unit_price", parseFloat(e.target.value) || 0)}
        sx={{ flex: { xs: "1 1 120px", sm: 1.2 } }}
        size="small"
        inputProps={{ min: 0, step: 0.01 }}
      />
      <Box sx={{ flex: { xs: "1 1 120px", sm: 1.2 }, display: "flex", alignItems: "center", px: 1.5, height: 40, borderRadius: 1, bgcolor: "rgba(255,240,240,0.5)" }}>
        <Typography variant="body2" fontWeight={600} sx={{ fontFeatureSettings: '"tnum"' }}>
          {currency} {lineTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </Typography>
      </Box>
      <IconButton size="small" onClick={() => onRemove(index)} disabled={!canRemove} sx={{ mt: 0.5 }}>
        <DeleteOutlineIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}
