"use client";

import { TextField, InputAdornment } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

interface Props {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function SearchInput({ value, onChange, placeholder = "Search..." }: Props) {
  return (
    <TextField
      size="small"
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      sx={{ minWidth: { xs: "100%", sm: 260 } }}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon fontSize="small" color="action" />
          </InputAdornment>
        ),
      }}
    />
  );
}
