"use client";

import { Box, Skeleton } from "@mui/material";

export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <Box>
      {Array.from({ length: rows }).map((_, i) => (
        <Box key={i} sx={{ display: "flex", gap: 2, mb: 1.5, px: 2, py: 1.5 }}>
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} variant="rounded" height={20} sx={{ flex: j === 0 ? 2 : 1, borderRadius: 1 }} />
          ))}
        </Box>
      ))}
    </Box>
  );
}

export function MetricSkeleton() {
  return (
    <Box sx={{ p: 3 }}>
      <Skeleton variant="text" width={80} height={16} />
      <Skeleton variant="text" width={120} height={32} sx={{ mt: 0.5 }} />
    </Box>
  );
}

export function CardSkeleton() {
  return (
    <Box sx={{ p: 3 }}>
      <Skeleton variant="text" width="60%" height={20} />
      <Skeleton variant="text" width="40%" height={16} sx={{ mt: 1 }} />
      <Skeleton variant="rounded" width="100%" height={100} sx={{ mt: 2, borderRadius: 1 }} />
    </Box>
  );
}
