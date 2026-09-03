"use client";
import { ShieldCheck, WandSparkles, Workflow } from "lucide-react";
import { UploadWorkspace } from "@/features/upload/upload-workspace";
import { RecentJobs } from "@/components/recent-jobs";
import { useT, type TranslationKey } from "@/lib/i18n";

export default function Home() {
  const { t } = useT();
  const features: { icon: typeof Workflow; label: TranslationKey }[] = [
    { icon: Workflow, label: "home.feature.worker" },
    { icon: ShieldCheck, label: "home.feature.qc" },
    { icon: WandSparkles, label: "home.feature.alpha" },
  ];
  return <>
    <div className="mb-8 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
      <div><p className="eyebrow mb-3">{t("home.eyebrow")}</p><h1 className="max-w-4xl text-4xl font-semibold tracking-[-.045em] sm:text-5xl">{t("home.title")}</h1><p className="mt-4 max-w-2xl text-base leading-7 text-black/55">{t("home.subtitle")}</p></div>
      <div className="hidden gap-5 rounded-2xl border border-black/[.06] bg-white/65 px-5 py-4 xl:flex">{features.map(({ icon: Icon, label }) => <span key={label} className="flex items-center gap-2 text-xs font-semibold text-black/50"><Icon size={16} className="text-moss" />{t(label)}</span>)}</div>
    </div>
    <UploadWorkspace /><RecentJobs />
  </>;
}