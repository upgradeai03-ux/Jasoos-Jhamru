import axios from 'axios';
import type {
  HealthStatus,
  ModelStatus,
  ImageDetectionResponse,
  EventRecord,
  AnalyticsData,
  DatasetSummary,
  DatasetInspectResult
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const getHealth = async (): Promise<HealthStatus> => {
  const res = await api.get<HealthStatus>('/health');
  return res.data;
};

export const getModelStatus = async (): Promise<ModelStatus> => {
  const res = await api.get<ModelStatus>('/model/status');
  return res.data;
};

export const detectImage = async (
  file: File,
  selectedBin: string = 'Dry Waste',
  confidenceThreshold: number = 0.35,
  logEvent: boolean = true
): Promise<ImageDetectionResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('selected_bin', selectedBin);
  formData.append('confidence_threshold', confidenceThreshold.toString());
  formData.append('log_event', logEvent ? 'true' : 'false');

  const res = await api.post<ImageDetectionResponse>('/detect/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const getEvents = async (
  limit: number = 200,
  sourceMode?: string,
  ruleResult?: string
): Promise<EventRecord[]> => {
  const params: Record<string, any> = { limit };
  if (sourceMode && sourceMode !== 'All') params.source_mode = sourceMode;
  if (ruleResult && ruleResult !== 'All') params.rule_result = ruleResult;

  const res = await api.get<EventRecord[]>('/events', { params });
  return res.data;
};

export const exportEventsCSVUrl = (): string => {
  return `${API_BASE_URL}/events/export`;
};

export const getAnalytics = async (): Promise<AnalyticsData> => {
  const res = await api.get<AnalyticsData>('/analytics');
  return res.data;
};

export const getDatasetSummary = async (): Promise<DatasetSummary> => {
  const res = await api.get<DatasetSummary>('/dataset/summary');
  return res.data;
};

export const getDatasetImages = async (split: string = 'test'): Promise<{ split: string; images: string[] }> => {
  const res = await api.get<{ split: string; images: string[] }>('/dataset/images', { params: { split } });
  return res.data;
};

export const inspectDatasetImage = async (
  split: string,
  imageName: string,
  selectedBin: string = 'Dry Waste',
  confidenceThreshold: number = 0.35
): Promise<DatasetInspectResult> => {
  const res = await api.get<DatasetInspectResult>('/dataset/inspect', {
    params: {
      split,
      image_name: imageName,
      selected_bin: selectedBin,
      confidence_threshold: confidenceThreshold
    }
  });
  return res.data;
};

export const getSegregationConfig = async () => {
  const res = await api.get('/config/segregation');
  return res.data;
};
