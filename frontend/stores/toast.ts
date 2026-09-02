import { create } from "zustand";

export type ToastTone = "success" | "error" | "info";
interface Toast { id: number; message: string; tone: ToastTone; }
interface ToastState { toasts: Toast[]; show: (message: string, tone?: ToastTone) => void; dismiss: (id: number) => void; }

export const useToast = create<ToastState>((set, get) => ({
  toasts: [],
  show: (message, tone = "info") => {
    const id = Date.now() + Math.random();
    set({ toasts: [...get().toasts, { id, message, tone }] });
    window.setTimeout(() => get().dismiss(id), 4200);
  },
  dismiss: (id) => set({ toasts: get().toasts.filter((toast) => toast.id !== id) }),
}));

