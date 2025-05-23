import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext"; // Import AuthProvider
import ClientNav from "@/components/ClientNav"; // Will create this next

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Analytics Dashboard",
  description: "AI Interview Analytics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50 text-gray-900`}
      >
        <AuthProvider>
          <ClientNav />
          <main className="p-4">
            {children}
          </main>
          <footer className="text-center p-4 text-xs text-gray-500">
            © {new Date().getFullYear()} Analytics Dashboard
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
