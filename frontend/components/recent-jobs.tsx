"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Clock3, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { localeTag, useT } from "@/lib/i18n";
import type { Job } from "@/types/api";
import { StatusBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function RecentJobs() {
  const [jobs, setJobs] = useState<Job[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const { t, lang } = useT();
  const load = useCallback(async () => { setLoading(true); setError(""); try { setJobs(await api.listJobs()); } catch (e) { setError(e instanceof Error ? e.message : "Backend unavailable"); } finally { setLoading(false); } }, []);
  useEffect(() => { const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer); }, [load]);
  return <section className="mt-10"><div className="mb-4 flex items-end justify-between"><div><p className="eyebrow mb-1">{t("recent.eyebrow")}</p><h2 className="text-xl font-semibold tracking-tight">{t("recent.title")}</h2></div><Button variant="ghost" size="sm" onClick={load}><RefreshCw size={14} /> {t("common.refresh")}</Button></div>
    {loading ? <div className="surface p-8 text-center text-sm text-black/45">{t("recent.loading")}</div> : error ? <div className="surface p-8 text-center"><p className="text-sm font-medium text-red-700">{t("recent.errorTitle")}</p><p className="mt-1 text-xs text-black/45">{error}</p><Button className="mt-4" variant="outline" onClick={load}>{t("common.retry")}</Button></div> : !jobs.length ? <div className="surface grid min-h-36 place-items-center p-8 text-center"><div><Clock3 className="mx-auto mb-2 text-black/25" /><p className="text-sm font-medium">{t("recent.emptyTitle")}</p><p className="mt-1 text-xs text-black/45">{t("recent.emptyHint")}</p></div></div> :
    <div className="surface divide-y divide-black/[.06] overflow-hidden">{jobs.slice(0, 8).map((job) => <Link href={`/jobs/${job.id}`} key={job.id} className="group flex items-center gap-4 px-5 py-4 hover:bg-lime/[.06]"><div className="min-w-0 flex-1"><div className="flex items-center gap-2"><p className="truncate text-sm font-semibold">{job.name}</p><StatusBadge status={job.status} /></div><p className="mt-1 text-xs text-black/45">{t("recent.counts", { total: job.total_images, completed: job.completed_images, review: job.review_images, failed: job.failed_images })}</p></div><time className="hidden text-xs text-black/40 sm:block">{new Date(job.created_at).toLocaleString(localeTag(lang))}</time><ArrowRight size={17} className="text-black/25 transition group-hover:translate-x-1 group-hover:text-moss" /></Link>)}</div>}
  </section>;
}