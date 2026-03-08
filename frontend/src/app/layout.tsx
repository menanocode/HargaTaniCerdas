import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HargaTaniCerdas — Prediksi Harga Bahan Pokok",
  description:
    "Sistem prediksi harga bahan pokok berbasis AI. Pantau tren harga beras, minyak goreng, telur, dan komoditas lainnya secara real-time.",
  keywords: [
    "harga bahan pokok",
    "prediksi harga",
    "AI",
    "beras",
    "minyak goreng",
    "telur",
    "Indonesia",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
