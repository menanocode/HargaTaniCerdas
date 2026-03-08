/**
 * API client for HargaTaniCerdas Backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

// ── Types ──────────────────────────────────────────

export interface PriceData {
  id: number;
  commodity: string;
  price: number;
  previous_price: number | null;
  change_percent: number | null;
  unit: string;
  region: string | null;
  date: string;
}

export interface PriceHistory {
  commodity: string;
  prices: PriceData[];
  avg_price: number;
  min_price: number;
  max_price: number;
}

export interface WeatherData {
  id: number;
  region: string | null;
  temperature: number | null;
  humidity: number | null;
  wind_speed: number | null;
  weather_desc: string | null;
  date: string;
}

export interface NewsData {
  id: number;
  title: string;
  url: string | null;
  source: string;
  sentiment_score: number | null;
  sentiment_label: string | null;
  related_commodity: string | null;
  date: string;
}

export interface MacroData {
  id: number;
  indicator: string;
  value: number;
  period: string | null;
  source: string;
  date: string;
}

export interface PredictionData {
  id: number;
  commodity: string;
  current_price: number | null;
  predicted_price: number;
  trend: string;
  change_percent: number | null;
  confidence: number | null;
  prediction_date: string;
  model_version: string;
}

export interface CommoditySummary {
  commodity: string;
  latest_price: number | null;
  previous_price: number | null;
  change_percent: number | null;
  trend: string | null;
  predicted_price: number | null;
}

export interface DashboardData {
  commodities: CommoditySummary[];
  latest_weather: WeatherData | null;
  latest_news: NewsData[];
  latest_macro: MacroData[];
  total_commodities: number;
  avg_change_percent: number | null;
}

// ── API Calls ──────────────────────────────────────

export async function getDashboard(
  kode_provinsi?: string,
  kode_kab_kota?: string,
  tanggal?: string
): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (kode_provinsi) params.append("kode_provinsi", kode_provinsi);
  if (kode_kab_kota) params.append("kode_kab_kota", kode_kab_kota);
  if (tanggal) params.append("tanggal", tanggal);

  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchAPI<DashboardData>(`/api/dashboard${query}`);
}

export async function getPriceHistory(
  commodity: string,
  days: number = 30,
  kode_provinsi?: string,
  kode_kab_kota?: string
): Promise<PriceHistory> {
  const params = new URLSearchParams({
    commodity,
    days: days.toString(),
  });
  if (kode_provinsi) params.append("kode_provinsi", kode_provinsi);
  if (kode_kab_kota) params.append("kode_kab_kota", kode_kab_kota);

  return fetchAPI<PriceHistory>(`/api/prices?${params.toString()}`);
}

export async function getPrediction(
  commodity: string,
  days: number = 7,
  kode_provinsi?: string,
  kode_kab_kota?: string
): Promise<PredictionData[]> {
  const params = new URLSearchParams({
    commodity,
    days: days.toString(),
  });
  if (kode_provinsi) params.append("kode_provinsi", kode_provinsi);
  if (kode_kab_kota) params.append("kode_kab_kota", kode_kab_kota);

  return fetchAPI<PredictionData[]>(`/api/predict?${params.toString()}`);
}

export async function getCommodities(): Promise<string[]> {
  return fetchAPI<string[]>("/api/commodities");
}

export async function getWeather(days: number = 7): Promise<WeatherData[]> {
  return fetchAPI<WeatherData[]>(`/api/weather?days=${days}`);
}

export async function getNews(
  days: number = 7,
  commodity?: string
): Promise<NewsData[]> {
  let url = `/api/news?days=${days}`;
  if (commodity) {
    url += `&commodity=${encodeURIComponent(commodity)}`;
  }
  return fetchAPI<NewsData[]>(url);
}

export async function triggerDataCollection(
  kode_provinsi?: string,
  kode_kab_kota?: string,
  tanggal?: string,
  tanggal_pembanding?: string
): Promise<{
  status: string;
  results: Record<string, string>;
}> {
  const params = new URLSearchParams();
  if (kode_provinsi) params.append("kode_provinsi", kode_provinsi);
  if (kode_kab_kota) params.append("kode_kab_kota", kode_kab_kota);
  if (tanggal) params.append("tanggal", tanggal);
  if (tanggal_pembanding) params.append("tanggal_pembanding", tanggal_pembanding);

  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchAPI(`/api/collect${query}`, { method: "POST" });
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}
