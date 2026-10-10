export interface DetectionItem {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  category: 'Wet Waste' | 'Dry Waste' | 'Needs Review';
  status: 'Correct Disposal' | 'Confirmed Violation' | 'Needs Review' | 'Uncertain';
  is_violation: boolean;
  is_correct: boolean;
  is_uncertain: boolean;
  reason: string;
}

export interface ImageDetectionResponse {
  success: boolean;
  detections: DetectionItem[];
  total_detected: number;
  inference_time_ms: number;
  selected_bin: string;
  has_violation: boolean;
  annotated_image_base64: string;
  image_dimensions: [number, number];
  model_name: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
}

export interface ModelStatus {
  is_loaded: boolean;
  model_name: string;
  model_path: string;
  total_classes: number;
  class_names: string[];
  load_error: string | null;
}

export interface EventRecord {
  event_id: number;
  timestamp: string;
  source_mode: string;
  detected_class: string;
  confidence: number;
  selected_bin: string;
  rule_category: string;
  rule_result: string;
  alert_status: string;
  snapshot_path: string | null;
}

export interface AnalyticsData {
  summary: {
    total_events: number;
    correct_events: number;
    confirmed_violations: number;
    needs_review_events: number;
    violation_rate_pct: number;
  };
  class_distribution: Record<string, number>;
  result_distribution: Record<string, number>;
}

export interface DatasetSummary {
  is_valid: boolean;
  num_classes: number;
  class_names: string[];
  splits: {
    train: number;
    valid: number;
    test: number;
  };
}

export interface DatasetInspectResult {
  image_name: string;
  split: string;
  prediction_overlay_base64: string;
  ground_truth_overlay_base64: string;
  metrics: {
    tp: number;
    fp: number;
    fn: number;
    precision: number;
    recall: number;
    mean_iou: number;
  };
  predictions: any[];
  ground_truths: any[];
}
