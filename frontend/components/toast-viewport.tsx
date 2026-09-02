"use client";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";
import { useToast } from "@/stores/toast";

const icons = { success: CheckCircle2, error: AlertCircle, info: Info };
export function ToastViewport() {
  const { toasts, dismiss } = useToast();
  return <div className="fixed bottom-5 right-5 z-50 flex w-[min(390px,calc(100vw-40px))] flex-col gap-2" aria-live="polite">
    {toasts.map((toast) => { const Icon = icons[toast.tone]; return (
      <div key={toast.id} className="flex items-start gap-3 rounded-xl border border-black/10 bg-ink p-4 text-sm text-white shadow-2xl">
        <Icon size={18} className={toast.tone === "success" ? "text-lime" : toast.tone === "error" ? "text-red-300" : "text-white/70"} />
        <span className="flex-1">{toast.message}</span><button onClick={() => dismiss(toast.id)} aria-label="Dismiss"><X size={16} /></button>
      </div>); })}
  </div>;
}

