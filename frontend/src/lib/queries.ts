import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "./api";
import type {
  Invoice, InvoiceCreate, InvoiceUpdate,
  Client, ClientListItem, ClientCreate, ClientUpdate,
  Payment, PaymentCreate, PaymentSummary,
  DashboardMetrics, Activity, UpcomingInvoice, StatusHistory,
} from "./types";

// ── Dashboard ──
export const useDashboardMetrics = () =>
  useQuery({ queryKey: ["dashboard", "metrics"], queryFn: () => api.get<DashboardMetrics>("/api/v1/dashboard/metrics").then((r) => r.data) });

export const useRecentActivity = (limit = 10) =>
  useQuery({ queryKey: ["dashboard", "activity", limit], queryFn: () => api.get<Activity[]>("/api/v1/dashboard/activity", { params: { limit } }).then((r) => r.data) });

export const useUpcomingInvoices = (days = 7) =>
  useQuery({ queryKey: ["dashboard", "upcoming", days], queryFn: () => api.get<UpcomingInvoice[]>("/api/v1/dashboard/upcoming", { params: { days } }).then((r) => r.data) });

// ── Invoices ──
export const useInvoices = (params?: { status?: string; search?: string }) =>
  useQuery({ queryKey: ["invoices", params], queryFn: () => api.get<Invoice[]>("/api/v1/invoices", { params }).then((r) => r.data) });

export const useInvoice = (id: string) =>
  useQuery({ queryKey: ["invoices", id], queryFn: () => api.get<Invoice>(`/api/v1/invoices/${id}`).then((r) => r.data), enabled: !!id });

export const useCreateInvoice = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data: InvoiceCreate) => api.post<Invoice>("/api/v1/invoices", data).then((r) => r.data), onSuccess: () => qc.invalidateQueries({ queryKey: ["invoices"] }) });
};

export const useUpdateInvoice = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data: InvoiceUpdate) => api.put<Invoice>(`/api/v1/invoices/${id}`, data).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["invoices"] }); qc.invalidateQueries({ queryKey: ["invoices", id] }); } });
};

export const useUpdateInvoiceStatus = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ status, notes }: { status: string; notes?: string }) => api.post(`/api/v1/invoices/${id}/status`, null, { params: { status, notes } }).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["invoices"] }); qc.invalidateQueries({ queryKey: ["invoices", id] }); } });
};

export const useSendInvoice = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: () => api.post(`/api/v1/invoices/${id}/send`).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["invoices"] }); qc.invalidateQueries({ queryKey: ["invoices", id] }); } });
};

export const usePayInvoice = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (notes?: string) => api.post(`/api/v1/invoices/${id}/pay`, null, { params: { notes } }).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["invoices"] }); qc.invalidateQueries({ queryKey: ["invoices", id] }); } });
};

export const useCancelInvoice = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (reason?: string) => api.post(`/api/v1/invoices/${id}/cancel`, null, { params: { reason } }).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["invoices"] }); qc.invalidateQueries({ queryKey: ["invoices", id] }); } });
};

export const useInvoiceHistory = (id: string) =>
  useQuery({ queryKey: ["invoices", id, "history"], queryFn: () => api.get<StatusHistory[]>(`/api/v1/invoices/${id}/history`).then((r) => r.data), enabled: !!id });

export const useExportInvoicePdf = () =>
  useMutation({ mutationFn: async (id: string) => { const r = await api.post(`/api/v1/invoices/${id}/export/pdf`, {}, { responseType: "blob" }); return r.data; } });

export const useExportInvoiceImage = () =>
  useMutation({ mutationFn: async ({ id, format }: { id: string; format: string }) => { const r = await api.post(`/api/v1/invoices/${id}/export/image`, {}, { params: { format }, responseType: "blob" }); return r.data; } });

export const useUploadLogo = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: async ({ id, file }: { id: string; file: File }) => { const fd = new FormData(); fd.append("logo", file); const r = await api.post(`/api/v1/invoices/${id}/logo`, fd, { headers: { "Content-Type": "multipart/form-data" } }); return r.data; }, onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["invoices", vars.id] }) });
};

// ── Clients ──
export const useClients = (search?: string) =>
  useQuery({ queryKey: ["clients", search], queryFn: () => api.get<ClientListItem[]>("/api/v1/clients", { params: { search } }).then((r) => r.data) });

export const useClient = (id: string) =>
  useQuery({ queryKey: ["clients", id], queryFn: () => api.get<Client>(`/api/v1/clients/${id}`).then((r) => r.data), enabled: !!id });

export const useClientInvoices = (id: string) =>
  useQuery({ queryKey: ["clients", id, "invoices"], queryFn: () => api.get<Invoice[]>(`/api/v1/clients/${id}/invoices`).then((r) => r.data), enabled: !!id });

export const useCreateClient = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data: ClientCreate) => api.post<Client>("/api/v1/clients", data).then((r) => r.data), onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }) });
};

export const useUpdateClient = (id: string) => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data: ClientUpdate) => api.put<Client>(`/api/v1/clients/${id}`, data).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["clients"] }); qc.invalidateQueries({ queryKey: ["clients", id] }); } });
};

export const useDeleteClient = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (id: string) => api.delete(`/api/v1/clients/${id}`), onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }) });
};

// ── Payments ──
export const usePayments = (params?: { invoice_id?: string }) =>
  useQuery({ queryKey: ["payments", params], queryFn: () => api.get("/api/v1/payments", { params }).then((r) => r.data) });

export const useInvoicePayments = (invoiceId: string) =>
  useQuery({ queryKey: ["payments", "invoice", invoiceId], queryFn: () => api.get<Payment[]>(`/api/v1/payments/invoice/${invoiceId}`).then((r) => r.data), enabled: !!invoiceId });

export const usePaymentSummary = () =>
  useQuery({ queryKey: ["payments", "summary"], queryFn: () => api.get<PaymentSummary>("/api/v1/payments/summary").then((r) => r.data) });

export const useCreatePayment = () => {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data: PaymentCreate) => api.post<Payment>("/api/v1/payments", data).then((r) => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ["payments"] }); qc.invalidateQueries({ queryKey: ["invoices"] }); } });
};

// ── Share ──
export const useShareInvoice = () =>
  useMutation({ mutationFn: ({ id, ...rest }: { id: string; email?: string; phone?: string; telegram_id?: number; message?: string }) => api.post(`/api/v1/invoices/${id}/share`, rest).then((r) => r.data) });
