import type { Metadata } from "next";
import Link from "next/link";
import { Aperture, Settings } from "lucide-react";
import { ToastViewport } from "@/components/toast-viewport";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Product Image Cleaner",
  description: "Batch background removal and quality control for e-commerce product imagery.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-black/[0.06] bg-white/75 backdrop-blur-xl">
          <div className="mx-auto flex h-16 max-w-[1520px] items-center justify-between px-5 lg:px-8">
            <Link href="/" className="focus-ring flex items-center gap-3 rounded-lg">
              <span className="grid size-9 place-items-center rounded-xl bg-ink text-lime"><Aperture size={19} /></span>
              <span>
                <span className="block text-sm font-semibold leading-tight">AI Product Image Cleaner</span>
                <span className="block text-[10px] font-medium uppercase tracking-[.14em] text-black/45">Production workspace</span>
              </span>
            </Link>
            <Link href="/settings" className="focus-ring flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-black/60 hover:bg-black/5 hover:text-ink">
              <Settings size={17} /> Settings
            </Link>
          </div>
        </header>
        <main className="mx-auto max-w-[1520px] px-5 py-8 lg:px-8 lg:py-10">{children}</main>
        <ToastViewport />
      </body>
    </html>
  );
}

