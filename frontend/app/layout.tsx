import type { Metadata } from "next";
import { ClientShell } from "@/components/client-shell";
import { ToastViewport } from "@/components/toast-viewport";
import { PREFERENCES_STORAGE_KEY } from "@/stores/preferences";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Product Image Cleaner",
  description: "Batch background removal and quality control for e-commerce product imagery.",
};

// Applies the persisted theme before first paint to avoid a flash of the wrong theme.
const themeInitScript = `
try {
  var stored = JSON.parse(localStorage.getItem(${JSON.stringify(PREFERENCES_STORAGE_KEY)}) || "{}");
  var state = stored.state || {};
  var theme = state.theme || "light";
  document.documentElement.dataset.theme = theme;
  if (theme === "custom") {
    var c = state.custom || {};
    var hex = function (value, fallback) {
      var v = /^#?[0-9a-fA-F]{6}$/.test(value || "") ? String(value).replace("#", "") : fallback;
      return [parseInt(v.slice(0, 2), 16), parseInt(v.slice(2, 4), 16), parseInt(v.slice(4, 6), 16)];
    };
    var mix = function (a, b, t) {
      return a.map(function (channel, i) { return Math.round(channel + (b[i] - channel) * t); }).join(" ");
    };
    var ink = hex(c.ink, "17221d"), paper = hex(c.paper, "fafbf8"), surface = hex(c.surface, "fffffc");
    var vars = {
      "--ink": ink.join(" "),
      "--muted": mix(ink, paper, 0.55),
      "--paper": paper.join(" "),
      "--surface": surface.join(" "),
      "--fog": mix(surface, ink, 0.045),
      "--line": mix(surface, ink, 0.14),
      "--brand": hex(c.brand, "2f6b4f").join(" "),
      "--accent": hex(c.accent, "c9f45b").join(" "),
      "--check": mix(surface, ink, 0.09),
      "--glow": "0.15"
    };
    for (var key in vars) document.documentElement.style.setProperty(key, vars[key]);
  }
} catch (error) {}
`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <ClientShell>{children}</ClientShell>
        <ToastViewport />
      </body>
    </html>
  );
}