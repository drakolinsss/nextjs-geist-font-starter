"use client";

import { Inter } from "next/font/google";
import { Toaster } from "react-hot-toast";
import { QueryClient, QueryClientProvider } from "react-query";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

// Create a client
const queryClient = new QueryClient();

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryClientProvider client={queryClient}>
          {children}
          <Toaster position="bottom-right" />
        </QueryClientProvider>
      </body>
    </html>
  );
}
