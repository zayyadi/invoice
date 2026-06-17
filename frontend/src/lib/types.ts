export interface User {
  id: string;
  email: string;
  full_name: string;
  company_name: string | null;
  phone: string | null;
  timezone: string;
  default_currency: string;
  email_verified: boolean;
  created_at: string;
}

export type InvoiceStatus = "draft" | "sent" | "viewed" | "partial" | "paid" | "overdue" | "cancelled";

export interface InvoiceItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface Invoice {
  id: string;
  user_id: string;
  invoice_number: string;
  status: InvoiceStatus;
  issuer_name: string | null;
  issuer_email: string | null;
  issuer_phone: string | null;
  issuer_address: string | null;
  payment_bank_name: string | null;
  payment_account_number: string | null;
  payment_account_name: string | null;
  customer_name: string;
  customer_email: string | null;
  issue_date: string;
  due_date: string;
  currency: string;
  notes: string | null;
  logo_path: string | null;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  items: InvoiceItem[];
  sent_at: string | null;
  viewed_at: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InvoiceCreate {
  invoice_number: string;
  client_id?: string | null;
  issuer_name?: string | null;
  issuer_email?: string | null;
  issuer_phone?: string | null;
  issuer_address?: string | null;
  payment_bank_name?: string | null;
  payment_account_number?: string | null;
  payment_account_name?: string | null;
  customer_name: string;
  customer_email?: string | null;
  issue_date: string;
  due_date: string;
  currency?: string;
  notes?: string | null;
  tax_rate?: number;
  items: { description: string; quantity: number; unit_price: number }[];
}

export interface InvoiceUpdate {
  invoice_number?: string;
  issuer_name?: string | null;
  issuer_email?: string | null;
  issuer_phone?: string | null;
  issuer_address?: string | null;
  payment_bank_name?: string | null;
  payment_account_number?: string | null;
  payment_account_name?: string | null;
  customer_name?: string;
  customer_email?: string | null;
  issue_date?: string;
  due_date?: string;
  currency?: string;
  notes?: string | null;
  tax_rate?: number;
}

export interface Client {
  id: string;
  user_id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  tax_id: string | null;
  notes: string | null;
  default_currency: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClientListItem {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  default_currency: string | null;
  invoice_count: number;
  total_invoiced: string;
  total_paid: string;
}

export interface ClientCreate {
  name: string;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  tax_id?: string | null;
  notes?: string | null;
  default_currency?: string | null;
}

export interface ClientUpdate {
  name?: string;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  tax_id?: string | null;
  notes?: string | null;
  default_currency?: string | null;
}

export interface Payment {
  id: string;
  invoice_id: string;
  user_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference_number: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaymentListItem {
  id: string;
  invoice_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference_number: string | null;
  invoice_number: string;
  customer_name: string;
}

export interface PaymentCreate {
  invoice_id: string;
  amount: number;
  payment_date?: string;
  payment_method?: string;
  reference_number?: string | null;
  notes?: string | null;
}

export interface PaymentSummary {
  total_payments: number;
  total_amount: number;
}

export interface DashboardMetrics {
  summary: {
    total_invoiced: number;
    total_paid: number;
    outstanding: number;
    overdue_amount: number;
    total_invoices: number;
    total_clients: number;
  };
  status_breakdown: Record<string, { count: number; total: number; paid: number }>;
  recent_activity: { payments_count: number; payments_total: number };
  overdue: {
    count: number;
    amount: number;
    invoices: { id: string; invoice_number: string; customer_name: string; due_date: string; amount: number; currency: string }[];
  };
  monthly_revenue: { month: string; revenue: number }[];
}

export interface Activity {
  id: string;
  type: string;
  description: string;
  amount: number;
  status?: string;
  invoice_id?: string;
  timestamp: string;
}

export interface UpcomingInvoice {
  id: string;
  invoice_number: string;
  customer_name: string;
  due_date: string;
  amount: number;
  currency: string;
  days_until_due: number;
}

export interface StatusHistory {
  id: string;
  status: string;
  changed_by: string | null;
  notes: string | null;
  created_at: string;
}
