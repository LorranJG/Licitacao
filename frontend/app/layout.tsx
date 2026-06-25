import type { Metadata } from "next";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Radar Licitações",
    template: "%s | Radar Licitações",
  },
  description: "Encontre licitações públicas em uma única plataforma.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen font-sans antialiased">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
