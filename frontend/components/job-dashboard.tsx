"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Download, ImageIcon, LoaderCircle, RefreshCw, SlidersHorizontal } from "lucide-react";
import { api } from "@/lib/api";
import { useT, type TranslationKey } from "@/lib/i18n";
import { formatDuration } from "@/lib/utils";
import { useToast } from "@/stores/toast";
import type { ImageAsset, Job } from "@/types/api";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeading } from "@/components/page-heading";

type Filter = "ALL" | "PROCESSING" | "COMPLETED" | "NEEDS_REVIEW" | "FAILED";
export function JobDashboard({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<Job | null>(null); const [images, setImages] = useState<ImageAsset[]>([]); const [error, setError] = useState("");
  const [filter, setFilter] = useState<Filter>("ALL"); const [sort, setSort] = useState("upload"); const toast = useToast();
  const { t } = useT();
  const load = useCallback(async () => { try { const [jobData, imageData] = await Promise.all([api.getJob(jobId), api.listImages(jobId)]); setJob(jobData); setImages(imageData); setError(""); } catch (e) { setError(e instanceof Error ? e.message : t("job.loadError")); } }, [jobId, t]);
  useEffect(() => { const initial = window.setTimeout(() => void load(), 0); const timer = window.setInterval(() => void load(), 1500); return () => { window.clearTimeout(initial); window.clearInterval(timer); }; }, [load]);
  const displayed = useMemo(() => images.filter((image) => filter === "ALL" || (filter === "PROCESSING" ? ["UPLOADED","QUEUED","PROCESSING"].includes(image.status) : image.status === filter)).sort((a,b) => sort === "quality" ? (b.quality_score ?? -1) - (a.quality_score ?? -1) : sort === "time" ? (b.processing_time_ms ?? -1) - (a.processing_time_ms ?? -1) : a.created_at.localeCompare(b.created_at)), [images, filter, sort]);
  if (error && !job) return <div className="surface p-10 text-center"><AlertTriangle className="mx-auto text-red-500" /><h1 className="mt-3 font-semibold">{t("job.errorTitle")}</h1><p className="mt-1 text-sm text-black/45">{error}</p><Button className="mt-5" onClick={load}>{t("common.retry")}</Button></div>;
  if (!job) return <div className="grid min-h-[50vh] place-items-center text-sm text-black/45"><LoaderCircle className="mr-2 inline animate-spin" /> {t("job.loading")}</div>;
  const finished = job.completed_images + job.review_images + job.failed_images; const progress = job.total_images ? Math.round((finished / job.total_images) * 100) : 0;
  const metrics: { label: TranslationKey; value: number }[] = [
    { label: "job.metric.total", value: job.total_images }, { label: "job.metric.queued", value: job.queued_images }, { label: "job.metric.processing", value: job.processing_images },
    { label: "job.metric.completed", value: job.completed_images }, { label: "job.metric.review", value: job.review_images }, { label: "job.metric.failed", value: job.failed_images },
  ];
  const filters: { id: Filter; label: string }[] = [
    { id: "ALL", label: t("job.filter.all") }, { id: "PROCESSING", label: t("status.PROCESSING") }, { id: "COMPLETED", label: t("status.COMPLETED") },
    { id: "NEEDS_REVIEW", label: t("status.NEEDS_REVIEW") }, { id: "FAILED", label: t("status.FAILED") },
  ];
  const sorts: { id: string; label: string }[] = [
    { id: "upload", label: t("job.sort.upload") }, { id: "quality", label: t("job.sort.quality") }, { id: "time", label: t("job.sort.time") },
  ];
  return <><PageHeading eyebrow={t("job.eyebrow", { id: job.id.slice(0,8).toUpperCase() })} title={job.name} description={t("job.description")} backHref="/" />
    <section className="surface p-5 lg:p-6"><div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">{metrics.map(({ label, value }) => <div key={label} className="rounded-xl bg-fog p-4"><p className="text-[11px] font-semibold uppercase tracking-wider text-black/40">{t(label)}</p><p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p></div>)}</div><div className="mt-5 flex items-center gap-4"><div className="flex-1"><Progress value={progress} /></div><span className="w-12 text-right text-sm font-semibold">{progress}%</span></div></section>
    <section className="mt-8"><div className="mb-4 flex flex-wrap items-center gap-2"><div className="flex flex-1 flex-wrap gap-2">{filters.map((item) => <button key={item.id} onClick={() => setFilter(item.id)} className={`focus-ring rounded-full px-3 py-2 text-xs font-semibold ${filter === item.id ? "bg-ink text-white" : "bg-white text-black/50 ring-1 ring-black/[.07] hover:text-ink"}`}>{item.label}</button>)}</div><SlidersHorizontal size={15} className="text-black/35" /><select value={sort} onChange={(e) => setSort(e.target.value)} className="focus-ring h-9 rounded-lg border border-black/10 bg-white px-3 text-xs font-semibold">{sorts.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select><Button variant="outline" size="sm" onClick={() => void load()}><RefreshCw size={14} /> {t("common.refresh")}</Button><Button size="sm" onClick={() => api.downloadJob(jobId,"all").catch((e) => toast.show(e.message,"error"))}><Download size={14} /> {t("job.downloadAll")}</Button></div>
      {!displayed.length ? <div className="surface grid min-h-56 place-items-center text-center"><div><ImageIcon className="mx-auto text-black/20" /><p className="mt-2 text-sm font-medium">{t("job.emptyTitle")}</p><p className="text-xs text-black/40">{t("job.emptyHint")}</p></div></div> : <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">{displayed.map((image) => <Link href={`/images/${image.id}`} key={image.id} className="surface group overflow-hidden transition hover:-translate-y-0.5 hover:shadow-xl"><div className="checkerboard relative aspect-square overflow-hidden"><img src={api.assetUrl(image.id,"thumbnail")} alt={image.original_filename} className="size-full object-contain transition duration-300 group-hover:scale-[1.025]" />{image.status === "PROCESSING" && <div className="processing-glow absolute inset-x-0 bottom-0 h-1 bg-blue-500" />}</div><div className="p-3"><p className="truncate text-xs font-semibold" title={image.original_filename}>{image.original_filename}</p><div className="mt-2 flex items-center justify-between gap-2"><StatusBadge status={image.status} /><span className="text-[11px] font-medium text-black/40">{image.quality_score == null ? "—" : `${image.quality_score}/100`}</span></div><p className="mt-2 text-[10px] text-black/35">{formatDuration(image.processing_time_ms)}</p></div></Link>)}</div>}
    </section></>;
}