"use client";
import { useParams } from "next/navigation";
import { JobDashboard } from "@/components/job-dashboard";
export default function JobPage() { const params = useParams<{ id: string }>(); return <JobDashboard jobId={params.id} />; }

