import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "./globals.css";
import ThemeProvider from "@/providers/ThemeProvider";
import QueryProvider from "@/providers/QueryProvider";

export const metadata: Metadata = {
  title: "Aura Invoice",
  description: "Beautiful invoice generator for small businesses",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
