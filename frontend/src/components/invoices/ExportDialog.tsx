"use client";

import { useState } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Box, Typography, CircularProgress, Alert, TextField,
} from "@mui/material";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import ImageIcon from "@mui/icons-material/Image";
import WhatsAppIcon from "@mui/icons-material/WhatsApp";
import { useExportInvoicePdf, useExportInvoiceImage, useShareInvoice } from "@/lib/queries";

interface Props {
  open: boolean;
  onClose: () => void;
  invoiceId: string;
  invoiceNumber: string;
}

export default function ExportDialog({ open, onClose, invoiceId, invoiceNumber }: Props) {
  const exportPdf = useExportInvoicePdf();
  const exportImage = useExportInvoiceImage();
  const shareInvoice = useShareInvoice();
  const [phone, setPhone] = useState("");
  const [shareResult, setShareResult] = useState<any>(null);

  const handleDownload = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePdf = async () => {
    const blob = await exportPdf.mutateAsync(invoiceId);
    handleDownload(blob, `invoice-${invoiceNumber}.pdf`);
  };

  const handleImage = async (format: string) => {
    const blob = await exportImage.mutateAsync({ id: invoiceId, format });
    handleDownload(blob, `invoice-${invoiceNumber}.${format}`);
  };

  const handleShare = async () => {
    if (!phone.trim()) return;
    const result = await shareInvoice.mutateAsync({ id: invoiceId, phone });
    setShareResult(result);
  };

  const isLoading = exportPdf.isPending || exportImage.isPending;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Export & Share</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Download invoice as PDF or image, or share via WhatsApp.
        </Typography>

        <Typography variant="subtitle1" sx={{ mb: 1.5 }}>
          Download
        </Typography>
        <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
          <Button variant="outlined" startIcon={exportPdf.isPending ? <CircularProgress size={16} /> : <PictureAsPdfIcon />} onClick={handlePdf} disabled={isLoading}>
            PDF
          </Button>
          <Button variant="outlined" startIcon={exportImage.isPending ? <CircularProgress size={16} /> : <ImageIcon />} onClick={() => handleImage("png")} disabled={isLoading}>
            PNG
          </Button>
          <Button variant="outlined" startIcon={exportImage.isPending ? <CircularProgress size={16} /> : <ImageIcon />} onClick={() => handleImage("jpg")} disabled={isLoading}>
            JPG
          </Button>
        </Box>

        <Typography variant="subtitle1" sx={{ mb: 1.5 }}>
          Share via WhatsApp
        </Typography>
        <Box sx={{ display: "flex", gap: 1.5, alignItems: "flex-start" }}>
          <TextField
            size="small"
            placeholder="Phone number (e.g. 2348012345678)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            sx={{ flex: 1 }}
          />
          <Button variant="contained" startIcon={<WhatsAppIcon />} onClick={handleShare} disabled={!phone.trim() || shareInvoice.isPending}>
            Generate Link
          </Button>
        </Box>
        {shareResult?.whatsapp_url && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ wordBreak: "break-all" }}>
              <a href={shareResult.whatsapp_url} target="_blank" rel="noopener noreferrer">
                Open WhatsApp Link
              </a>
            </Typography>
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
