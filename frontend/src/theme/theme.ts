"use client";

import { createTheme } from "@mui/material/styles";
import type { Shadows } from "@mui/material/styles";

const aura = {
  bg: "#fff8f7",
  bgDeep: "#fff0f0",
  surface: "#ffffff",
  surfaceHigh: "#fee9ea",
  surfaceHighest: "#f2dedf",
  primary: "#a1354c",
  primaryLight: "#ffd9dd",
  primaryDark: "#400012",
  primaryHover: "#851f38",
  secondary: "#864e57",
  secondaryLight: "#feb6c0",
  tertiary: "#36645c",
  tertiaryLight: "#bcece1",
  outline: "#897173",
  outlineVariant: "#dcc0c2",
  warning: "#e6a817",
  danger: "#ba1a1a",
  errorLight: "#ffdad6",
  textPrimary: "#24191a",
  textSecondary: "#564244",
};

const theme = createTheme({
  palette: {
    primary: { main: aura.primary, light: aura.primaryLight, dark: aura.primaryHover, contrastText: "#ffffff" },
    secondary: { main: aura.secondary, light: aura.secondaryLight, dark: "#6b3740", contrastText: "#ffffff" },
    success: { main: aura.tertiary, light: aura.tertiaryLight },
    warning: { main: aura.warning },
    error: { main: aura.danger, light: aura.errorLight, dark: "#93000a" },
    info: { main: "#0277bd" },
    background: { default: aura.bg, paper: aura.surface },
    text: { primary: aura.textPrimary, secondary: aura.textSecondary },
    divider: aura.outlineVariant,
    action: { hover: "rgba(161, 53, 76, 0.04)", selected: "rgba(161, 53, 76, 0.08)" },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: { fontSize: 32, fontWeight: 700, lineHeight: 1.2, letterSpacing: 0 },
    h2: { fontSize: 24, fontWeight: 600, lineHeight: 1.3, letterSpacing: 0 },
    h3: { fontSize: 18, fontWeight: 600, lineHeight: 1.33 },
    h5: { fontSize: 16, fontWeight: 600, lineHeight: 1.33 },
    h6: { fontSize: 14, fontWeight: 600, lineHeight: 1.25 },
    body1: { fontSize: 18, fontWeight: 400, lineHeight: 1.55 },
    body2: { fontSize: 16, fontWeight: 400, lineHeight: 1.5 },
    subtitle1: { fontSize: 14, fontWeight: 600, lineHeight: 1.43, letterSpacing: "0.05em", textTransform: "uppercase" as const },
    caption: { fontSize: 12, fontWeight: 600, lineHeight: 1.33, letterSpacing: "0.05em" },
    button: { fontSize: 14, fontWeight: 600, lineHeight: 1.2, letterSpacing: "0.02em", textTransform: "none" as const },
    overline: { fontSize: 12, fontWeight: 600, lineHeight: 1.33, letterSpacing: "0.08em", textTransform: "uppercase" as const },
  },
  shape: { borderRadius: 8 },
  spacing: 8,
  shadows: [
    "none",
    "0 1px 3px rgba(131,115,116,0.08)",
    "0 2px 6px rgba(131,115,116,0.08)",
    "0 4px 12px rgba(131,115,116,0.08)",
    "0 4px 20px rgba(131,115,116,0.1)",
    "0 8px 24px rgba(131,115,116,0.1)",
    "0 12px 32px rgba(131,115,116,0.12)",
    "0 16px 40px rgba(131,115,116,0.12)",
    "0 20px 48px rgba(131,115,116,0.14)",
    "0 24px 56px rgba(131,115,116,0.14)",
    "0 28px 64px rgba(131,115,116,0.16)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
    "0 30px 80px rgba(0,0,0,0.32)",
  ] as Shadows,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { background: `linear-gradient(180deg, ${aura.bg} 0%, ${aura.bgDeep} 100%)`, minHeight: "100vh" },
        "*": { boxSizing: "border-box" as const },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 4, minHeight: 44, padding: "8px 20px" },
        contained: {
          backgroundColor: aura.primary,
          color: "#ffffff",
          boxShadow: `0 2px 8px rgba(161,53,76,0.25)`,
          "&:hover": { backgroundColor: aura.primaryHover, boxShadow: `0 4px 12px rgba(161,53,76,0.35)`, transform: "translateY(-1px)" },
        },
        outlined: {
          borderColor: aura.outlineVariant,
          "&:hover": { borderColor: aura.outline, backgroundColor: "rgba(254,233,234,0.5)" },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: "none", borderRadius: 8 },
        elevation0: { boxShadow: "0 1px 3px rgba(131,115,116,0.08)" },
        elevation1: { boxShadow: "0 4px 20px rgba(131,115,116,0.1)", border: `1px solid ${aura.outlineVariant}` },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: `1px solid ${aura.outlineVariant}`,
          boxShadow: "0 4px 20px rgba(131,115,116,0.1)",
          backgroundImage: "none",
        },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small", variant: "outlined" },
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 4,
            backgroundColor: "rgba(255,255,255,0.95)",
            "& fieldset": { borderColor: aura.outlineVariant },
            "&:hover fieldset": { borderColor: aura.outline },
            "&.Mui-focused fieldset": { borderColor: aura.primary, borderWidth: 2, boxShadow: `0 0 0 3px rgba(161,53,76,0.12)` },
          },
          "& .MuiInputLabel-root": { color: aura.textSecondary },
          "& .MuiInputLabel-root.Mui-focused": { color: aura.primary },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6, fontWeight: 600, fontSize: 12 },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          "& .MuiTableCell-head": {
            fontWeight: 700,
            fontSize: 12,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color: aura.textSecondary,
            backgroundColor: aura.surfaceHigh,
            borderBottom: `1px solid ${aura.outlineVariant}`,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: aura.outlineVariant, fontSize: 14 },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 8,
          boxShadow: "0 30px 80px rgba(0,0,0,0.32)",
          backgroundImage: "none",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "rgba(255,248,247,0.88)",
          backdropFilter: "blur(18px)",
          boxShadow: "0 1px 0 rgba(220,192,194,0.4)",
          color: aura.textPrimary,
        },
      },
    },
  },
});

export { aura };
export default theme;
