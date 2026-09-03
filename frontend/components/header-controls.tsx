"use client";
import { useEffect, useRef, useState } from "react";
import { Check, Languages, Palette, RotateCcw } from "lucide-react";
import { useT } from "@/lib/i18n";
import {
  DEFAULT_CUSTOM_THEME,
  usePreferences,
  type CustomTheme,
  type Language,
  type ThemeName,
} from "@/stores/preferences";

function usePopover() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);
  return { open, setOpen, ref };
}

const popoverButton =
  "focus-ring grid size-9 place-items-center rounded-lg text-black/60 transition hover:bg-black/5 hover:text-ink";

function ThemeMenu() {
  const { t } = useT();
  const theme = usePreferences((state) => state.theme);
  const custom = usePreferences((state) => state.custom);
  const setTheme = usePreferences((state) => state.setTheme);
  const setCustomColor = usePreferences((state) => state.setCustomColor);
  const resetCustom = usePreferences((state) => state.resetCustom);
  const { open, setOpen, ref } = usePopover();

  const themes: { id: ThemeName; label: string; swatch: string }[] = [
    { id: "light", label: t("menu.theme.light"), swatch: "#fafbf8" },
    { id: "dark", label: t("menu.theme.dark"), swatch: "#141a16" },
    { id: "custom", label: t("menu.theme.custom"), swatch: custom.paper },
  ];
  const colorFields: { key: keyof CustomTheme; label: string }[] = [
    { key: "paper", label: t("menu.theme.paper") },
    { key: "surface", label: t("menu.theme.surface") },
    { key: "ink", label: t("menu.theme.ink") },
    { key: "brand", label: t("menu.theme.brand") },
    { key: "accent", label: t("menu.theme.accent") },
  ];

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        aria-label={t("menu.theme")}
        aria-expanded={open}
        title={t("menu.theme")}
        onClick={() => setOpen(!open)}
        className={popoverButton}
      >
        <Palette size={17} />
      </button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-60 rounded-xl border border-black/[0.08] bg-white p-2 text-sm text-ink shadow-xl">
          <p className="px-2 pb-1 pt-1 text-[10px] font-bold uppercase tracking-[0.14em] text-black/40">{t("menu.theme")}</p>
          {themes.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTheme(item.id)}
              className="focus-ring flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left text-xs font-semibold hover:bg-black/5"
            >
              <span className="size-4 rounded-full ring-1 ring-inset ring-black/15" style={{ backgroundColor: item.swatch }} />
              <span className="flex-1">{item.label}</span>
              {theme === item.id && <Check size={14} className="text-moss" />}
            </button>
          ))}
          <div className="mt-1 border-t border-black/[0.07] pt-2">
            <div className="flex items-center justify-between px-2 pb-1">
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-black/40">{t("menu.theme.customColors")}</p>
              <button
                type="button"
                aria-label={t("menu.theme.reset")}
                title={t("menu.theme.reset")}
                onClick={() => { resetCustom(); setTheme("custom"); }}
                className="focus-ring rounded-md p-1 text-black/40 hover:bg-black/5 hover:text-ink"
              >
                <RotateCcw size={13} />
              </button>
            </div>
            {colorFields.map(({ key, label }) => (
              <label key={key} className="flex cursor-pointer items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs font-medium hover:bg-black/5">
                <span>{label}</span>
                <input
                  type="color"
                  value={custom[key] ?? DEFAULT_CUSTOM_THEME[key]}
                  onChange={(event) => { setCustomColor(key, event.target.value); setTheme("custom"); }}
                  className="h-6 w-9 cursor-pointer rounded border border-black/10 bg-transparent p-0.5"
                />
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function LanguageMenu() {
  const { t } = useT();
  const lang = usePreferences((state) => state.lang);
  const setLang = usePreferences((state) => state.setLang);
  const { open, setOpen, ref } = usePopover();
  const languages: { id: Language; label: string; short: string }[] = [
    { id: "en", label: "English", short: "EN" },
    { id: "zh", label: "中文", short: "中" },
  ];

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        aria-label={t("menu.language")}
        aria-expanded={open}
        title={t("menu.language")}
        onClick={() => setOpen(!open)}
        className={popoverButton}
      >
        <Languages size={17} />
      </button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-40 rounded-xl border border-black/[0.08] bg-white p-2 text-sm text-ink shadow-xl">
          <p className="px-2 pb-1 pt-1 text-[10px] font-bold uppercase tracking-[0.14em] text-black/40">{t("menu.language")}</p>
          {languages.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => { setLang(item.id); setOpen(false); }}
              className="focus-ring flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left text-xs font-semibold hover:bg-black/5"
            >
              <span className="grid size-4 place-items-center rounded bg-fog text-[9px] font-bold text-black/60">{item.short}</span>
              <span className="flex-1">{item.label}</span>
              {lang === item.id && <Check size={14} className="text-moss" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function HeaderControls() {
  return (
    <div className="flex items-center gap-1">
      <ThemeMenu />
      <LanguageMenu />
    </div>
  );
}