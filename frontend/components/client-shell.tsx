"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Aperture, Settings } from "lucide-react";
import { HeaderControls } from "@/components/header-controls";
import { localeTag, useT } from "@/lib/i18n";
import { applyTheme, usePreferences } from "@/stores/preferences";

/**
 * Client shell: applies the persisted theme to <html> after mount and renders
 * the localized header. SSR always ships English + light theme so hydration matches.
 */
export function ClientShell({ children }: { children: React.ReactNode }) {
  const { t, lang } = useT();
  const theme = usePreferences((state) => state.theme);
  const custom = usePreferences((state) => state.custom);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  useEffect(() => {
    if (!mounted) return;
    applyTheme(theme, custom);
  }, [mounted, theme, custom]);
  useEffect(() => {
    document.documentElement.lang = localeTag(lang);
  }, [lang]);

  return (
    <>
      <header className="border-b border-black/[0.06] bg-white/75 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1520px] items-center justify-between px-5 lg:px-8">
          <Link href="/" className="focus-ring flex items-center gap-3 rounded-lg">
            <span className="grid size-9 place-items-center rounded-xl bg-ink text-lime"><Aperture size={19} /></span>
            <span>
              <span className="block text-sm font-semibold leading-tight">AI Product Image Cleaner</span>
              <span className="block text-[10px] font-medium uppercase tracking-[.14em] text-black/45">{t("header.subtitle")}</span>
            </span>
          </Link>
          <div className="flex items-center gap-1">
            <HeaderControls />
            <Link href="/settings" className="focus-ring flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-black/60 hover:bg-black/5 hover:text-ink">
              <Settings size={17} /> {t("header.settings")}
            </Link>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1520px] px-5 py-8 lg:px-8 lg:py-10">{children}</main>
    </>
  );
}