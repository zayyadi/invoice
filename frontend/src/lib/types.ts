export type InvoiceItemInput = {
  description: string;
  quantity: number;
  unit_price: number;
};

export type InvoiceCreatePayload = {
  invoice_number: string;
  customer_name: string;
  customer_email?: string;
  issue_date: string;
  due_date: string;
  currency: "NGN";
  notes?: string;
  tax_rate: number;
  items: InvoiceItemInput[];
};

export type InvoiceItem = InvoiceItemInput & {
  id: number;
  line_total: string;
};

export type Invoice = {
  id: string;
  invoice_number: string;
  customer_name: string;
  customer_email?: string;
  issue_date: string;
  due_date: string;
  currency: string;
  notes?: string;
  logo_path?: string;
  subtotal: string;
  tax_amount: string;
  total_amount: string;
  items: InvoiceItem[];
};
