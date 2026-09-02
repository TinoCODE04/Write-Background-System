import { cn } from "@/lib/utils";
import type { ImageStatus } from "@/types/api";

const styles: Record<string, string> = {
  COMPLETED: "bg-emerald-50 text-emerald-700 ring-emerald-600/15", NEEDS_REVIEW: "bg-amber-50 text-amber-700 ring-amber-600/20",
  FAILED: "bg-red-50 text-red-700 ring-red-600/15", PROCESSING: "bg-blue-50 text-blue-700 ring-blue-600/15",
  QUEUED: "bg-slate-100 text-slate-600 ring-slate-600/10", UPLOADED: "bg-violet-50 text-violet-700 ring-violet-600/15"
};
export function StatusBadge({ status }: { status: ImageStatus | string }) {
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-bold tracking-[.08em] ring-1 ring-inset", styles[status] ?? styles.QUEUED)}>{status.replace("_", " ")}</span>;
}

