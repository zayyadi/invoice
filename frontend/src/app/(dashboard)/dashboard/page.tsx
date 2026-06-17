"use client";

import { Box, Grid, Typography } from "@mui/material";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import PaymentsIcon from "@mui/icons-material/Payments";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { useDashboardMetrics, useRecentActivity, useUpcomingInvoices } from "@/lib/queries";
import MetricCard from "@/components/dashboard/MetricCard";
import StatusBreakdown from "@/components/dashboard/StatusBreakdown";
import RevenueChart from "@/components/dashboard/RevenueChart";
import UpcomingInvoices from "@/components/dashboard/UpcomingInvoices";
import RecentActivity from "@/components/dashboard/RecentActivity";
import { MetricSkeleton, CardSkeleton } from "@/components/common/LoadingSkeleton";

export default function DashboardPage() {
  const { data: metrics, isLoading } = useDashboardMetrics();
  const { data: activities } = useRecentActivity();
  const { data: upcoming } = useUpcomingInvoices();

  return (
    <Box>
      <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Overview of your invoicing activity
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {isLoading ? (
          <>
            <Grid item xs={12} sm={6} md={3}><MetricSkeleton /></Grid>
            <Grid item xs={12} sm={6} md={3}><MetricSkeleton /></Grid>
            <Grid item xs={12} sm={6} md={3}><MetricSkeleton /></Grid>
            <Grid item xs={12} sm={6} md={3}><MetricSkeleton /></Grid>
          </>
        ) : metrics ? (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Total Invoiced"
                value={`NGN ${metrics.summary.total_invoiced.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                icon={<ReceiptLongIcon />}
                subtitle={`${metrics.summary.total_invoices} invoices`}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Total Paid"
                value={`NGN ${metrics.summary.total_paid.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                icon={<PaymentsIcon />}
                color="success.main"
                subtitle={`${metrics.recent_activity.payments_count} payments (30d)`}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Outstanding"
                value={`NGN ${metrics.summary.outstanding.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                icon={<AccountBalanceWalletIcon />}
                color="warning.main"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Overdue"
                value={`NGN ${metrics.summary.overdue_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                icon={<WarningAmberIcon />}
                color="error.main"
                subtitle={`${metrics.overdue.count} invoices`}
              />
            </Grid>
          </>
        ) : null}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {isLoading ? <CardSkeleton /> : metrics && <RevenueChart data={metrics.monthly_revenue} />}
        </Grid>
        <Grid item xs={12} md={4}>
          {isLoading ? <CardSkeleton /> : metrics && <StatusBreakdown breakdown={metrics.status_breakdown} />}
        </Grid>
        <Grid item xs={12} md={6}>
          {isLoading ? <CardSkeleton /> : upcoming && <UpcomingInvoices invoices={upcoming} />}
        </Grid>
        <Grid item xs={12} md={6}>
          {isLoading ? <CardSkeleton /> : activities && <RecentActivity activities={activities} />}
        </Grid>
      </Grid>
    </Box>
  );
}
