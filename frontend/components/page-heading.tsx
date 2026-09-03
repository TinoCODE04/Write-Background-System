"use client";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useT } from "@/lib/i18n";

export function PageHeading({ eyebrow, title, description, backHref }: { eyebrow: string; title: string; description?: string; backHref?: string }) {
  const { t } = useT();
  return <div className="mb-7">
    {backHref && <Link href={backHref} className="mb-4 inline-flex items-center gap-1.5 text-xs font-semibold text-black/50 hover:text-moss"><ArrowLeft size={14} /> {t("common.back")}</Link>}
    <p className="eyebrow mb-2">{eyebrow}</p><h1 className="text-3xl font-semibold tracking-[-.035em] lg:text-4xl">{title}</h1>
    {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-black/55 lg:text-base">{description}</p>}
  </div>;
}