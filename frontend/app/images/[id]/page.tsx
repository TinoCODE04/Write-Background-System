"use client";
import { useParams } from "next/navigation";
import { ImageDetail } from "@/components/image-detail";
export default function ImagePage() { const params = useParams<{ id: string }>(); return <ImageDetail imageId={params.id} />; }

