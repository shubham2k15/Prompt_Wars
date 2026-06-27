import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MindGarden AI",
  description: "A mental wellness companion for students preparing for high-pressure exams."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
