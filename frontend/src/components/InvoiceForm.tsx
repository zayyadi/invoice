"use client";

import { useFieldArray, useForm } from "react-hook-form";
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { createInvoice } from "@/lib/api";
import { Invoice, InvoiceCreatePayload } from "@/lib/types";

type Props = {
  onCreated: (invoice: Invoice) => void;
};

const today = new Date().toISOString().split("T")[0];

export default function InvoiceForm({ onCreated }: Props) {
  const { register, control, handleSubmit, formState } = useForm<InvoiceCreatePayload>({
    defaultValues: {
      invoice_number: "INV-0001",
      customer_name: "",
      customer_email: "",
      issue_date: today,
      due_date: today,
      currency: "NGN",
      notes: "",
      tax_rate: 0,
      items: [{ description: "", quantity: 1, unit_price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Create Invoice
        </Typography>

        <Box
          component="form"
          onSubmit={handleSubmit(async (payload) => {
            const created = await createInvoice(payload);
            onCreated(created);
          })}
        >
          <Stack spacing={2}>
            <TextField label="Invoice Number" {...register("invoice_number", { required: true })} />
            <TextField label="Bill To (Name)" {...register("customer_name", { required: true })} />
            <TextField label="Bill To Email" {...register("customer_email")} />
            <Grid container spacing={2}>
              <Grid size={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Issue Date"
                  InputLabelProps={{ shrink: true }}
                  {...register("issue_date", { required: true })}
                />
              </Grid>
              <Grid size={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Due Date"
                  InputLabelProps={{ shrink: true }}
                  {...register("due_date", { required: true })}
                />
              </Grid>
            </Grid>
            <TextField value="NGN (Naira)" disabled />
            <TextField type="number" label="Tax Rate (%)" {...register("tax_rate", { valueAsNumber: true })} />

            <Typography variant="subtitle1">Items</Typography>
            {fields.map((field, index) => (
              <Grid key={field.id} container spacing={1}>
                <Grid size={5}>
                  <TextField
                    fullWidth
                    label="Description"
                    {...register(`items.${index}.description`, { required: true })}
                  />
                </Grid>
                <Grid size={2}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Qty"
                    {...register(`items.${index}.quantity`, { valueAsNumber: true, min: 1 })}
                  />
                </Grid>
                <Grid size={3}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Unit Price (₦)"
                    {...register(`items.${index}.unit_price`, { valueAsNumber: true, min: 0 })}
                  />
                </Grid>
                <Grid size={2}>
                  <Button color="error" onClick={() => remove(index)}>
                    Remove
                  </Button>
                </Grid>
              </Grid>
            ))}
            <Button
              variant="outlined"
              onClick={() => append({ description: "", quantity: 1, unit_price: 0 })}
            >
              Add Item
            </Button>

            <TextField multiline minRows={2} label="Notes" {...register("notes")} />

            <Button type="submit" variant="contained" disabled={formState.isSubmitting}>
              Create Invoice
            </Button>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}
