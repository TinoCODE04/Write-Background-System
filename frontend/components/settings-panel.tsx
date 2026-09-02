"use client";
import { useCallback, useEffect, useState } from "react";
import { Cpu, Database, FolderOpen, Gauge, HardDrive, LoaderCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { SystemInfo } from "@/types/api";
import { Button } from "@/components/ui/button";

export function SettingsPanel() {
  const [info,setInfo] = useState<SystemInfo | null>(null); const [error,setError] = useState("");
  const load = useCallback(async () => { setError(""); try { setInfo(await api.system()); } catch(e) { setError(e instanceof Error ? e.message : "Backend unavailable"); } }, []);
  useEffect(() => { const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer); }, [load]);
  if (!info && !error) return <div className="surface grid min-h-64 place-items-center text-sm text-black/45"><LoaderCircle className="animate-spin" /> Reading backend configuration…</div>;
  if (error) return <div className="surface p-10 text-center"><p className="font-semibold text-red-700">Could not read system settings</p><p className="mt-1 text-sm text-black/45">{error}</p><Button className="mt-4" onClick={load}>Retry</Button></div>;
  const rows = [
    [Cpu,"Current AI model",info!.model_name,"Loaded once by the image worker"],
    [Gauge,"Current device",info!.device,"Automatically selected at worker startup"],
    [Database,"Database",info!.database,"Persistent local job and image metadata"],
    [FolderOpen,"Storage location",info!.storage_location,"Originals and generated assets"],
    [HardDrive,"Upload limit",`${info!.max_upload_mb} MB per image`,`Configurable with MAX_UPLOAD_MB`],
    [Gauge,"Quality threshold",`${info!.quality_threshold} / 100`,`Lower scores are routed to manual review`]
  ] as const;
  return <div className="surface divide-y divide-black/[.06] overflow-hidden">{rows.map(([Icon,label,value,detail]) => <div key={label} className="grid gap-3 p-5 sm:grid-cols-[44px_1fr_1.2fr] sm:items-center"><span className="grid size-10 place-items-center rounded-xl bg-fog text-moss"><Icon size={18} /></span><div><p className="text-sm font-semibold">{label}</p><p className="mt-0.5 text-xs text-black/40">{detail}</p></div><p className="break-all rounded-lg bg-fog px-3 py-2 text-xs font-medium sm:text-right">{value}</p></div>)}</div>;
}
