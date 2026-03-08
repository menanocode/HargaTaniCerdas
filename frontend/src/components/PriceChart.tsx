"use client";

import React from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from "recharts";
import { PriceData, PredictionData, formatCurrency } from "@/lib/api";

interface PriceChartProps {
    priceHistory: PriceData[];
    predictions: PredictionData[];
    commodity: string;
}

interface ChartDataPoint {
    date: string;
    price: number | null;
    predicted: number | null;
    label: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
        <div
            className="glass-card p-3 shadow-xl"
            style={{ border: "1px solid var(--border-glow)" }}
        >
            <p
                className="text-xs font-medium mb-2"
                style={{ color: "var(--text-muted)" }}
            >
                {label}
            </p>
            {payload.map((entry: any, index: number) => (
                <div key={index} className="flex items-center gap-2">
                    <div
                        className="w-2 h-2 rounded-full"
                        style={{ background: entry.color }}
                    />
                    <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                        {entry.name}:
                    </span>
                    <span className="text-xs font-bold" style={{ color: entry.color }}>
                        {formatCurrency(entry.value)}
                    </span>
                </div>
            ))}
        </div>
    );
};

export default function PriceChart({
    priceHistory,
    predictions,
    commodity,
}: PriceChartProps) {
    // Combine price history and predictions into one dataset
    const chartData: ChartDataPoint[] = [];

    // Add historical prices
    for (const p of priceHistory) {
        chartData.push({
            date: p.date,
            price: p.price,
            predicted: null,
            label: new Date(p.date).toLocaleDateString("id-ID", {
                day: "numeric",
                month: "short",
            }),
        });
    }

    // Add prediction data points (connect with last actual price)
    if (predictions.length > 0 && priceHistory.length > 0) {
        // Bridge point: last actual price also as prediction start
        const lastActual = priceHistory[priceHistory.length - 1];
        chartData[chartData.length - 1].predicted = lastActual.price;
    }

    for (const p of predictions) {
        chartData.push({
            date: p.prediction_date,
            price: null,
            predicted: p.predicted_price,
            label: new Date(p.prediction_date).toLocaleDateString("id-ID", {
                day: "numeric",
                month: "short",
            }),
        });
    }

    const allValues = chartData
        .map((d) => d.price || d.predicted || 0)
        .filter((v) => v > 0);
    const minVal = Math.min(...allValues) * 0.95;
    const maxVal = Math.max(...allValues) * 1.05;

    return (
        <div className="glass-card p-6 animate-fade-in-up delay-200" style={{ opacity: 0, animationFillMode: "forwards" }}>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
                        Grafik Harga{" "}
                        <span className="gradient-text">
                            {commodity.charAt(0).toUpperCase() + commodity.slice(1)}
                        </span>
                    </h3>
                    <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                        Harga historis & prediksi AI
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                        <div className="w-3 h-1 rounded-full" style={{ background: "var(--accent-emerald)" }} />
                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                            Historis
                        </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-3 h-1 rounded-full" style={{ background: "var(--accent-cyan)" }} />
                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                            Prediksi
                        </span>
                    </div>
                </div>
            </div>

            <div style={{ width: "100%", height: 320 }}>
                {chartData.length > 0 ? (
                    <ResponsiveContainer>
                        <AreaChart
                            data={chartData}
                            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                        >
                            <defs>
                                <linearGradient id="gradientPrice" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                                    <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient
                                    id="gradientPredicted"
                                    x1="0"
                                    y1="0"
                                    x2="0"
                                    y2="1"
                                >
                                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.3} />
                                    <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="label"
                                tick={{ fontSize: 11 }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <YAxis
                                domain={[minVal, maxVal]}
                                tick={{ fontSize: 11 }}
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={(v) =>
                                    new Intl.NumberFormat("id-ID", {
                                        notation: "compact",
                                    }).format(v)
                                }
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="price"
                                stroke="#10b981"
                                fill="url(#gradientPrice)"
                                strokeWidth={2.5}
                                dot={false}
                                activeDot={{ r: 5, fill: "#10b981", stroke: "#fff", strokeWidth: 2 }}
                                name="Harga Aktual"
                                connectNulls={false}
                            />
                            <Area
                                type="monotone"
                                dataKey="predicted"
                                stroke="#06b6d4"
                                fill="url(#gradientPredicted)"
                                strokeWidth={2.5}
                                strokeDasharray="6 3"
                                dot={false}
                                activeDot={{ r: 5, fill: "#06b6d4", stroke: "#fff", strokeWidth: 2 }}
                                name="Prediksi AI"
                                connectNulls={false}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                            Belum ada data. Klik &quot;Refresh Data&quot; untuk mengumpulkan data.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
