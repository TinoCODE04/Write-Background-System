import { create } from "zustand";
interface UploadState { files: File[]; setFiles: (files: File[]) => void; remove: (key: string) => void; clear: () => void; }
const keyOf = (file: File) => `${file.name}-${file.size}-${file.lastModified}`;
export const useUploadStore = create<UploadState>((set) => ({
  files: [], setFiles: (incoming) => set((state) => {
    const known = new Set(state.files.map(keyOf)); return { files: [...state.files, ...incoming.filter((file) => !known.has(keyOf(file)))] };
  }), remove: (key) => set((state) => ({ files: state.files.filter((file) => keyOf(file) !== key) })), clear: () => set({ files: [] })
}));
export { keyOf };

