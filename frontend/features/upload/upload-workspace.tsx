"use client";
import { useCallback, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useDropzone, type FileRejection } from "react-dropzone";
import { FileImage, Sparkles, Trash2, UploadCloud } from "lucide-react";
import { api } from "@/lib/api";
import { formatBytes } from "@/lib/utils";
import { keyOf, useUploadStore } from "@/stores/upload";
import { useToast } from "@/stores/toast";
import { Button } from "@/components/ui/button";

const ACCEPT = { "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"] };
export function UploadWorkspace() {
  const router = useRouter(); const toast = useToast(); const { files, setFiles, remove, clear } = useUploadStore();
  const [busy, setBusy] = useState(false);
  const totalSize = useMemo(() => files.reduce((sum, file) => sum + file.size, 0), [files]);
  const onDrop = useCallback((accepted: File[], rejected: FileRejection[]) => {
    setFiles(accepted);
    if (rejected.length) toast.show(`${rejected.length} file${rejected.length > 1 ? "s were" : " was"} rejected. Use JPG, PNG, or WEBP under 50 MB.`, "error");
  }, [setFiles, toast]);
  const dropzone = useDropzone({ onDrop, accept: ACCEPT, multiple: true, maxSize: 50 * 1024 * 1024 });

  async function processImages() {
    if (!files.length) return;
    setBusy(true);
    try {
      const job = await api.createJob();
      const result = await api.uploadImages(job.id, files);
      if (result.errors.length) toast.show(`${result.errors.length} image${result.errors.length > 1 ? "s" : ""} could not be added.`, "error");
      await api.processJob(job.id); clear(); router.push(`/jobs/${job.id}`);
    } catch (error) { toast.show(error instanceof Error ? error.message : "Could not create the batch.", "error"); }
    finally { setBusy(false); }
  }

  return <section className="surface overflow-hidden">
    <div {...dropzone.getRootProps()} className={`group m-3 grid min-h-[300px] cursor-pointer place-items-center rounded-xl border border-dashed p-8 text-center transition ${dropzone.isDragActive ? "border-moss bg-lime/15" : "border-black/15 bg-fog/70 hover:border-moss/60 hover:bg-lime/[.08]"}`}>
      <input {...dropzone.getInputProps()} />
      <div>
        <span className="mx-auto mb-5 grid size-14 place-items-center rounded-2xl bg-ink text-lime shadow-lg"><UploadCloud size={25} /></span>
        <h2 className="text-xl font-semibold tracking-tight">{dropzone.isDragActive ? "Release to add images" : "Drag product images here"}</h2>
        <p className="mt-1 text-sm text-black/50">or click to browse · select as many as you need</p>
        <div className="mt-5 flex justify-center gap-2">{["JPG", "JPEG", "PNG", "WEBP"].map((type) => <span key={type} className="rounded-md bg-white px-2 py-1 text-[10px] font-bold tracking-wider text-black/45 ring-1 ring-black/5">{type}</span>)}</div>
      </div>
    </div>
    <div className="border-t border-black/[.06] p-5 lg:px-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div><p className="text-sm font-semibold">Selected {files.length} image{files.length === 1 ? "" : "s"}</p><p className="mt-0.5 text-xs text-black/45">Total size: {formatBytes(totalSize)}</p></div>
        <div className="flex gap-2">{files.length > 0 && <Button variant="ghost" onClick={clear}><Trash2 size={16} /> Clear</Button>}<Button variant="accent" size="lg" disabled={!files.length || busy} onClick={processImages}><Sparkles size={17} /> {busy ? "Creating batch…" : "Process images"}</Button></div>
      </div>
      {files.length > 0 && <div className="mt-4 max-h-36 overflow-auto rounded-xl border border-black/[.06] bg-white">
        {files.slice(0, 40).map((file) => <div key={keyOf(file)} className="flex items-center gap-3 border-b border-black/[.05] px-3 py-2.5 last:border-0"><FileImage size={16} className="text-moss" /><span className="min-w-0 flex-1 truncate text-xs font-medium">{file.name}</span><span className="text-[11px] text-black/40">{formatBytes(file.size)}</span><button aria-label={`Remove ${file.name}`} onClick={() => remove(keyOf(file))} className="rounded-md p-1 text-black/35 hover:bg-red-50 hover:text-red-600"><Trash2 size={14} /></button></div>)}
        {files.length > 40 && <p className="p-3 text-center text-xs text-black/45">and {files.length - 40} more</p>}
      </div>}
    </div>
  </section>;
}
