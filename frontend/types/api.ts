export type ImageStatus = "UPLOADED" | "QUEUED" | "PROCESSING" | "COMPLETED" | "NEEDS_REVIEW" | "FAILED";
export interface Job {
  id: string; name: string; status: string; total_images: number; queued_images: number; processing_images: number;
  completed_images: number; review_images: number; failed_images: number; created_at: string; updated_at: string; completed_at: string | null;
}
export interface ProcessingSettings {
  edge_cleanup: number; feather: number; remove_halo: boolean; remove_small_islands: boolean; fill_holes: boolean;
  mask_smoothness: number; keep_natural_shadow: boolean; erosion: number; dilation: number;
  min_component_area: number; max_hole_area: number; background_color: string;
}
export interface ImageAsset {
  id: string; job_id: string; original_filename: string; width: number; height: number; file_size: number; mime_type: string;
  status: ImageStatus; quality_score: number | null; quality_flags: string[]; processing_time_ms: number | null;
  model_name: string | null; model_version: string | null; processing_settings: ProcessingSettings & { source_sha256?: string };
  error_message: string | null; approved_at: string | null; created_at: string; updated_at: string;
}
export interface UploadResponse { uploaded: ImageAsset[]; errors: { filename: string; error: string }[]; }
export interface SystemInfo { model_name: string; model_version: string; device: string; database: string; storage_location: string; quality_threshold: number; max_upload_mb: number; }

