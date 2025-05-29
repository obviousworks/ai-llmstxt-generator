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
  title: "LLMs.txt Generator - Automated Documentation for AI Models",
  description: "Generate llms.txt files automatically from any website. Create AI-friendly documentation that helps Large Language Models understand your site content with structured navigation, key page descriptions, and curated resources.",
  keywords: ["llms.txt", "AI documentation", "website crawling", "machine learning", "documentation generator", "LLM", "artificial intelligence"],
  authors: [{ name: "LLMs.txt Generator" }],
  creator: "LLMs.txt Generator",
  publisher: "LLMs.txt Generator",
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
    title: 'LLMs.txt Generator - Automated Documentation for AI Models',
    description: 'Generate llms.txt files automatically from any website. Create AI-friendly documentation that helps Large Language Models understand your site content.',
    siteName: 'LLMs.txt Generator',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LLMs.txt Generator - Automated Documentation for AI Models',
    description: 'Generate llms.txt files automatically from any website. Create AI-friendly documentation that helps Large Language Models understand your site content.',
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://llm-txt-generator.vercel.app'),
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
