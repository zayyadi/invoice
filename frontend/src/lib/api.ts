import { Invoice, InvoiceCreatePayload } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function createInvoice(payload: InvoiceCreatePayload): Promise<Invoice> {
  const response = await fetch(`${API_URL}/api/v1/invoices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Create invoice failed: ${response.status}`);
  }

  return response.json();
}

export async function getInvoice(invoiceId: string): Promise<Invoice> {
  const response = await fetch(`${API_URL}/api/v1/invoices/${invoiceId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Fetch invoice failed: ${response.status}`);
  }
  return response.json();
}

export async function uploadLogo(invoiceId: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append("logo", file);

  const response = await fetch(`${API_URL}/api/v1/invoices/${invoiceId}/logo`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Logo upload failed: ${response.status}`);
  }
}

export async function exportInvoice(invoiceId: string, type: "pdf" | "png" | "jpg"): Promise<void> {
  const endpoint =
    type === "pdf"
      ? `${API_URL}/api/v1/invoices/${invoiceId}/export/pdf`
      : `${API_URL}/api/v1/invoices/${invoiceId}/export/image?format=${type}`;

  const response = await fetch(endpoint, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Export failed: ${response.status}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `invoice-${invoiceId}.${type}`;
  link.click();
  URL.revokeObjectURL(url);
}

export { API_URL };
