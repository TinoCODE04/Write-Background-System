import { ShieldCheck, WandSparkles, Workflow } from "lucide-react";
import { UploadWorkspace } from "@/features/upload/upload-workspace";
import { RecentJobs } from "@/components/recent-jobs";

export default function Home() {
  return <>
    <div className="mb-8 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
      <div><p className="eyebrow mb-3">Clean product assets, at scale</p><h1 className="max-w-4xl text-4xl font-semibold tracking-[-.045em] sm:text-5xl">Batch remove backgrounds and create clean e-commerce product images.</h1><p className="mt-4 max-w-2xl text-base leading-7 text-black/55">Drop a shoot, let the worker process every file, then review only the results that need a human eye.</p></div>
      <div className="hidden gap-5 rounded-2xl border border-black/[.06] bg-white/65 px-5 py-4 xl:flex">{[[Workflow,"Independent worker"],[ShieldCheck,"Automatic QC"],[WandSparkles,"Continuous alpha"]].map(([Icon,label]) => { const I = Icon as typeof Workflow; return <span key={label as string} className="flex items-center gap-2 text-xs font-semibold text-black/50"><I size={16} className="text-moss" />{label as string}</span>; })}</div>
    </div>
    <UploadWorkspace /><RecentJobs />
  </>;
}

