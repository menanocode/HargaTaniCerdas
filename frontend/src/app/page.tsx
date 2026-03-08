"use client";

import React, { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import StatsOverview from "@/components/StatsOverview";
import CommoditySelector from "@/components/CommoditySelector";
import RegionSelector from "@/components/RegionSelector";
import PriceChart from "@/components/PriceChart";
import PredictionCard from "@/components/PredictionCard";
import CommodityTable from "@/components/CommodityTable";
import NewsPanel from "@/components/NewsPanel";
import WeatherPanel from "@/components/WeatherPanel";
import {
  getDashboard,
  getPriceHistory,
  getPrediction,
  triggerDataCollection,
  DashboardData,
  PriceData,
  PredictionData,
} from "@/lib/api";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [priceHistory, setPriceHistory] = useState<PriceData[]>([]);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState<string>("beras");
  const [kodeProvinsi, setKodeProvinsi] = useState<string>("33");
  const [kodeKabKota, setKodeKabKota] = useState<string>("3315");

  // Set default dates based on today and 5 days ago
  const getTodayStr = () => new Date().toISOString().split("T")[0];
  const getDaysAgoStr = (days: number) => {
    const d = new Date();
    d.setDate(d.getDate() - days);
    return d.toISOString().split("T")[0];
  };

  const [tanggal, setTanggal] = useState<string>(getTodayStr());
  const [tanggalPembanding, setTanggalPembanding] = useState<string>(getDaysAgoStr(5));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);
  const [collectResult, setCollectResult] = useState<string | null>(null);

  // Fetch dashboard data
  const fetchDashboard = useCallback(async () => {
    try {
      const data = await getDashboard(kodeProvinsi, kodeKabKota, tanggal);
      setDashboard(data);

      // Auto-select first commodity if available
      if (data.commodities.length > 0 && !data.commodities.find(c => c.commodity === selectedCommodity)) {
        setSelectedCommodity(data.commodities[0].commodity);
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
      setError("Gagal memuat dashboard. Pastikan backend sudah berjalan di port 8000.");
    }
  }, [selectedCommodity, kodeProvinsi, kodeKabKota, tanggal]);

  // Fetch commodity-specific data
  const fetchCommodityData = useCallback(async (commodity: string) => {
    try {
      const [history, preds] = await Promise.allSettled([
        getPriceHistory(commodity, 30, kodeProvinsi, kodeKabKota),
        getPrediction(commodity, 7, kodeProvinsi, kodeKabKota),
      ]);

      if (history.status === "fulfilled") {
        setPriceHistory(history.value.prices);
      } else {
        setPriceHistory([]);
      }

      if (preds.status === "fulfilled") {
        setPredictions(preds.value);
      } else {
        setPredictions([]);
      }
    } catch (err) {
      console.error("Commodity data fetch error:", err);
    }
  }, [kodeProvinsi, kodeKabKota]);

  // Handle refresh - collect data then reload
  const handleRefresh = async () => {
    setIsCollecting(true);
    setCollectResult(null);
    setError(null);

    try {
      const result = await triggerDataCollection(kodeProvinsi, kodeKabKota, tanggal, tanggalPembanding);
      const summary = Object.entries(result.results)
        .map(([k, v]) => `${k}: ${v}`)
        .join(", ");
      setCollectResult(`Data berhasil dikumpulkan! ${summary}`);

      // Reload all data
      await fetchDashboard();
      await fetchCommodityData(selectedCommodity);
    } catch (err) {
      setError("Gagal mengumpulkan data. Pastikan backend dan SP2KP API berjalan.");
    } finally {
      setIsCollecting(false);
      // Auto-hide success message
      setTimeout(() => setCollectResult(null), 8000);
    }
  };

  // Handle select commodity
  const handleSelectCommodity = (commodity: string) => {
    setSelectedCommodity(commodity);
  };

  // Handle region/date apply
  const handleApplyRegion = (prov: string, kab: string, tgl: string, tglP: string) => {
    setKodeProvinsi(prov);
    setKodeKabKota(kab);
    setTanggal(tgl);
    setTanggalPembanding(tglP);
    // Data will automatically refetch due to useEffect dependencies on these states
  };

  // Initial load
  useEffect(() => {
    setIsLoading(true);
    fetchDashboard().finally(() => setIsLoading(false));
  }, [fetchDashboard]);

  // Load commodity data when selection changes
  useEffect(() => {
    if (selectedCommodity) {
      fetchCommodityData(selectedCommodity);
    }
  }, [selectedCommodity, fetchCommodityData]);

  const commodityNames = dashboard?.commodities.map((c) => c.commodity) || [];

  return (
    <div className="min-h-screen relative" style={{ zIndex: 1 }}>
      <Navbar onRefresh={handleRefresh} isLoading={isCollecting} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Error / Success Messages */}
        {error && (
          <div
            className="p-4 rounded-xl text-sm animate-fade-in-up"
            style={{
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.2)",
              color: "#fca5a5",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {collectResult && (
          <div
            className="p-4 rounded-xl text-sm animate-fade-in-up"
            style={{
              background: "rgba(16, 185, 129, 0.1)",
              border: "1px solid rgba(16, 185, 129, 0.2)",
              color: "#6ee7b7",
            }}
          >
            ✅ {collectResult}
          </div>
        )}

        {/* Stats Overview */}
        <StatsOverview
          commodities={dashboard?.commodities || []}
          totalCommodities={dashboard?.total_commodities || 0}
          avgChangePercent={dashboard?.avg_change_percent ?? null}
        />

        {/* Region & Commodity Selectors */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <RegionSelector
            kodeProvinsi={kodeProvinsi}
            kodeKabKota={kodeKabKota}
            tanggal={tanggal}
            tanggalPembanding={tanggalPembanding}
            onApply={handleApplyRegion}
            isLoading={isLoading || isCollecting}
          />

          {commodityNames.length > 0 && (
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
                Pilih Komoditas:
              </span>
              <div className="w-64">
                <CommoditySelector
                  commodities={commodityNames}
                  selected={selectedCommodity}
                  onSelect={handleSelectCommodity}
                />
              </div>
            </div>
          )}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart - 2 columns */}
          <div className="lg:col-span-2">
            <PriceChart
              priceHistory={priceHistory}
              predictions={predictions}
              commodity={selectedCommodity}
            />
          </div>

          {/* Prediction Card - 1 column */}
          <div>
            <PredictionCard
              predictions={predictions}
              commodity={selectedCommodity}
            />
          </div>
        </div>

        {/* Commodity Table */}
        <CommodityTable
          commodities={dashboard?.commodities || []}
          selected={selectedCommodity}
          onSelect={handleSelectCommodity}
        />

        {/* Bottom Grid: News + Weather */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <NewsPanel news={dashboard?.latest_news || []} />
          <WeatherPanel
            weather={dashboard?.latest_weather ?? null}
            macroData={dashboard?.latest_macro || []}
          />
        </div>

        {/* Footer */}
        <footer className="text-center py-8" style={{ borderTop: "1px solid var(--border-subtle)" }}>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            HargaTaniCerdas © {new Date().getFullYear()} — Sistem Prediksi Harga Bahan Pokok Berbasis AI
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
            Data dari SP2KP, BMKG, CNN Indonesia, BPS
          </p>
        </footer>
      </main>
    </div>
  );
}
