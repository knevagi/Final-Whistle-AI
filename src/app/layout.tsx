import type { Metadata } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Final Whistle AI | Premier League News, Match Reports & Analysis",
  description: "Your premier destination for English football coverage. Get the latest Premier League news, in-depth match reports, expert analysis, and trending topics from the world of football.",
  keywords: "football, premier league, match reports, football analysis, football news, soccer, manchester united, liverpool, arsenal, chelsea",
  authors: [{ name: "Final Whistle AI Editorial Team" }],
  openGraph: {
    title: "Final Whistle AI - Premier League Coverage",
    description: "Latest Premier League news, match reports, and expert football analysis",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
