"use client";

import { Button } from "@mui/material";

import { uploadLogo } from "@/lib/api";

type Props = {
  invoiceId: string;
  onUploaded: () => void;
};

export default function LogoUploader({ invoiceId, onUploaded }: Props) {
  return (
    <Button component="label" variant="outlined">
      Upload Company Logo
      <input
        hidden
        type="file"
        accept=".png,.jpg,.jpeg,.svg"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) return;
          await uploadLogo(invoiceId, file);
          onUploaded();
        }}
      />
    </Button>
  );
}
