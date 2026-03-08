"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus, Brain, Target } from "lucide-react";
import { PredictionData, formatCurrency, formatPercent } from "@/lib/api";

interface PredictionCardProps {
    predictions: PredictionData[];
    commodity: string;
}

export default function PredictionCard({
    predictions,
    commodity,
}: PredictionCardProps) {
    if (!predictions || predictions.length === 0) {
        return (
            <div className="glass-card p-6 animate-fade-in-up delay-300" style={{ opacity: 0, animationFillMode: "forwards" }}>
                <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5" style={{ color: "var(--accent-cyan)" }} />
                    <h3 className="text-lg font-semibold">Prediksi AI</h3>
                </div>
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    Belum ada prediksi. Kumpulkan data terlebih dahulu.
                </p>
            </div>
        );
    }

    // Use first prediction for main display
    const firstPred = predictions[0];
    const lastPred = predictions[predictions.length - 1];

    // Overall trend based on change from current to last predicted
    const overallChange =
        firstPred.current_price && lastPred.predicted_price
            ? ((lastPred.predicted_price - firstPred.current_price) /
                firstPred.current_price) *
            100
            : 0;

    const trendIcon =
        overallChange > 1 ? (
            <TrendingUp className="w-6 h-6" />
        ) : overallChange < -1 ? (
            <TrendingDown className="w-6 h-6" />
        ) : (
            <Minus className="w-6 h-6" />
        );

    const trendLabel =
        overallChange > 1 ? "Naik" : overallChange < -1 ? "Turun" : "Stabil";
    const trendBadge =
        overallChange > 1
            ? "badge-naik"
            : overallChange < -1
                ? "badge-turun"
                : "badge-stabil";

    return (
        <div className="glass-card p-6 animate-fade-in-up delay-300" style={{ opacity: 0, animationFillMode: "forwards" }}>
            <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5" style={{ color: "var(--accent-cyan)" }} />
                    <h3 className="text-lg font-semibold">Prediksi AI</h3>
                </div>
                <span className="text-xs px-2 py-1 rounded-lg" style={{ background: "rgba(6, 182, 212, 0.1)", color: "var(--accent-cyan)" }}>
                    {firstPred.model_version}
                </span>
            </div>

            {/* Main prediction display */}
            <div className="text-center mb-6">
                <div className="flex items-center justify-center gap-2 mb-2">
                    <span className={`p-2 rounded-xl ${trendBadge}`}>{trendIcon}</span>
                </div>
                <p className="text-3xl font-bold mb-1">
                    {formatCurrency(lastPred.predicted_price)}
                </p>
                <div className="flex items-center justify-center gap-2">
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full ${trendBadge}`}>
                        {trendLabel} {formatPercent(overallChange)}
                    </span>
                </div>
                <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
                    Prediksi {predictions.length} hari ke depan
                </p>
            </div>

            {/* Current vs Predicted */}
            <div className="grid grid-cols-2 gap-3 mb-5">
                <div className="p-3 rounded-xl" style={{ background: "rgba(255, 255, 255, 0.03)" }}>
                    <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>
                        Harga Saat Ini
                    </p>
                    <p className="text-sm font-bold" style={{ color: "var(--text-primary)" }}>
                        {firstPred.current_price
                            ? formatCurrency(firstPred.current_price)
                            : "-"}
                    </p>
                </div>
                <div className="p-3 rounded-xl" style={{ background: "rgba(255, 255, 255, 0.03)" }}>
                    <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>
                        Prediksi Akhir
                    </p>
                    <p className="text-sm font-bold" style={{ color: "var(--accent-cyan)" }}>
                        {formatCurrency(lastPred.predicted_price)}
                    </p>
                </div>
            </div>

            {/* Confidence */}
            {firstPred.confidence !== null && (
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-1.5">
                            <Target className="w-3.5 h-3.5" style={{ color: "var(--text-muted)" }} />
                            <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                                Tingkat Keyakinan
                            </span>
                        </div>
                        <span className="text-xs font-semibold" style={{ color: "var(--accent-emerald)" }}>
                            {firstPred.confidence?.toFixed(1)}%
                        </span>
                    </div>
                    <div className="w-full h-2 rounded-full" style={{ background: "rgba(255, 255, 255, 0.06)" }}>
                        <div
                            className="h-full rounded-full transition-all duration-1000 ease-out"
                            style={{
                                width: `${Math.min(100, firstPred.confidence || 0)}%`,
                                background: "var(--gradient-primary)",
                            }}
                        />
                    </div>
                </div>
            )}

            {/* Day-by-day mini predictions */}
            <div className="mt-5">
                <p className="text-xs font-medium mb-3" style={{ color: "var(--text-muted)" }}>
                    Detail Per Hari
                </p>
                <div className="space-y-2 max-h-44 overflow-y-auto">
                    {predictions.map((p, i) => (
                        <div
                            key={i}
                            className="flex items-center justify-between px-3 py-2 rounded-lg transition-colors"
                            style={{ background: "rgba(255, 255, 255, 0.02)" }}
                        >
                            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                                {new Date(p.prediction_date).toLocaleDateString("id-ID", {
                                    weekday: "short",
                                    day: "numeric",
                                    month: "short",
                                })}
                            </span>
                            <div className="flex items-center gap-2">
                                <span className="text-xs font-medium">
                                    {formatCurrency(p.predicted_price)}
                                </span>
                                <span
                                    className={`text-xs px-1.5 py-0.5 rounded ${p.trend === "naik"
                                            ? "badge-naik"
                                            : p.trend === "turun"
                                                ? "badge-turun"
                                                : "badge-stabil"
                                        }`}
                                >
                                    {p.change_percent !== null ? formatPercent(p.change_percent) : "-"}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
