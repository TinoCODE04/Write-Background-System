import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemeName = "light" | "dark" | "custom";
export type Language = "en" | "zh";

export interface CustomTheme {
  paper: string;
  surface: string;
  ink: string;
  brand: string;
  accent: string;
}

export const DEFAULT_CUSTOM_THEME: CustomTheme = {
  paper: "#fafbf8",
  surface: "#fffffc",
  ink: "#17221d",
  brand: "#2f6b4f",
  accent: "#c9f45b",
};

interface PreferencesState {
  theme: ThemeName;
  custom: CustomTheme;
  lang: Language;
  setTheme: (theme: ThemeName) => void;
  setCustomColor: (key: keyof CustomTheme, hex: string) => void;
  resetCustom: () => void;
  setLang: (lang: Language) => void;
}

export const PREFERENCES_STORAGE_KEY = "apic-preferences";

export const usePreferences = create<PreferencesState>()(
  persist(
    (set) => ({
      theme: "light",
      custom: DEFAULT_CUSTOM_THEME,
      lang: "en",
      setTheme: (theme) => set({ theme }),
      setCustomColor: (key, hex) => set((state) => ({ custom: { ...state.custom, [key]: hex } })),
      resetCustom: () => set({ custom: DEFAULT_CUSTOM_THEME }),
      setLang: (lang) => set({ lang }),
    }),
    { name: PREFERENCES_STORAGE_KEY }
  )
);

function hexToTriplet(hex: string): [number, number, number] {
  const value = hex.replace("#", "");
  const full = value.length === 3 ? value.split("").map((c) => c + c).join("") : value;
  const num = Number.parseInt(full, 16);
  if (Number.isNaN(num) || full.length !== 6) return [0, 0, 0];
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function mixTriplet(a: [number, number, number], b: [number, number, number], t: number): string {
  const mix = a.map((channel, i) => Math.round(channel + (b[i] - channel) * t));
  return mix.join(" ");
}

/** Inline custom-theme CSS variables on <html>; clear them for preset themes. */
export function applyCustomThemeVars(custom: CustomTheme, target: HTMLElement = document.documentElement) {
  const ink = hexToTriplet(custom.ink);
  const paper = hexToTriplet(custom.paper);
  const surface = hexToTriplet(custom.surface);
  const vars: Record<string, string> = {
    "--ink": ink.join(" "),
    "--muted": mixTriplet(ink, paper, 0.55),
    "--paper": paper.join(" "),
    "--surface": surface.join(" "),
    "--fog": mixTriplet(surface, ink, 0.045),
    "--line": mixTriplet(surface, ink, 0.14),
    "--brand": hexToTriplet(custom.brand).join(" "),
    "--accent": hexToTriplet(custom.accent).join(" "),
    "--check": mixTriplet(surface, ink, 0.09),
    "--glow": "0.15",
  };
  for (const [key, value] of Object.entries(vars)) target.style.setProperty(key, value);
}

export function clearCustomThemeVars(target: HTMLElement = document.documentElement) {
  for (const key of ["--ink", "--muted", "--paper", "--surface", "--fog", "--line", "--brand", "--accent", "--check", "--glow"]) {
    target.style.removeProperty(key);
  }
}

export function applyTheme(theme: ThemeName, custom: CustomTheme) {
  const root = document.documentElement;
  root.dataset.theme = theme;
  if (theme === "custom") applyCustomThemeVars(custom, root);
  else clearCustomThemeVars(root);
}