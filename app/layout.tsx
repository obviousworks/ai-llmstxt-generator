import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LLMs.txt Generator - by ObviousWorks | Let the LLMs eat your content!",
  description: "Enhanced AI-powered llms.txt generator with sitemap-first crawling, FAQ detection, and intelligent content processing. Automated documentation extraction for Large Language Models - let the LLMs eat your content!",
  keywords: ["llms.txt", "AI documentation", "website crawling", "machine learning", "documentation generator", "LLM", "artificial intelligence", "ObviousWorks", "sitemap crawling", "FAQ extraction"],
  authors: [{ name: "ObviousWorks" }],
  creator: "ObviousWorks",
  publisher: "ObviousWorks",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    title: 'LLMs.txt Generator - by ObviousWorks | Let the LLMs eat your content!',
    description: 'Enhanced AI-powered llms.txt generator with sitemap-first crawling, FAQ detection, and intelligent content processing - let the LLMs eat your content!',
    siteName: 'LLMs.txt Generator - by ObviousWorks',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LLMs.txt Generator - by ObviousWorks | Let the LLMs eat your content!',
    description: 'Enhanced AI-powered llms.txt generator with sitemap-first crawling, FAQ detection, and intelligent content processing - let the LLMs eat your content!',
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
