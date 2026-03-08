"use client";

import React from "react";
import {
    TrendingUp,
    TrendingDown,
    Minus,
    Package,
    BarChart3,
} from "lucide-react";
import { CommoditySummary, formatCurrency, formatPercent } from "@/lib/api";

interface StatsOverviewProps {
    commodities: CommoditySummary[];
    totalCommodities: number;
    avgChangePercent: number | null;
}

export default function StatsOverview({
    commodities,
    totalCommodities,
    avgChangePercent,
}: StatsOverviewProps) {
    const naikCount = commodities.filter(
        (c) => c.change_percent !== null && c.change_percent > 0
    ).length;
    const turunCount = commodities.filter(
        (c) => c.change_percent !== null && c.change_percent < 0
    ).length;
    const stabilCount = totalCommodities - naikCount - turunCount;

    const stats = [
        {
            label: "Total Komoditas",
            value: totalCommodities.toString(),
            icon: Package,
            color: "var(--accent-cyan)",
            bg: "rgba(6, 182, 212, 0.1)",
            border: "rgba(6, 182, 212, 0.2)",
        },
        {
            label: "Harga Naik",
            value: naikCount.toString(),
            icon: TrendingUp,
            color: "var(--accent-red)",
            bg: "rgba(239, 68, 68, 0.1)",
            border: "rgba(239, 68, 68, 0.2)",
        },
        {
            label: "Harga Turun",
            value: turunCount.toString(),
            icon: TrendingDown,
            color: "var(--accent-emerald)",
            bg: "rgba(16, 185, 129, 0.1)",
            border: "rgba(16, 185, 129, 0.2)",
        },
        {
            label: "Rata-rata Perubahan",
            value: avgChangePercent !== null ? formatPercent(avgChangePercent) : "-",
            icon: BarChart3,
            color: "var(--accent-amber)",
            bg: "rgba(245, 158, 11, 0.1)",
            border: "rgba(245, 158, 11, 0.2)",
        },
    ];

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat, i) => (
                <div
                    key={stat.label}
                    className="glass-card p-5 animate-fade-in-up"
                    style={{ animationDelay: `${i * 0.1}s`, opacity: 0, animationFillMode: "forwards" }}
                >
                    <div className="flex items-center justify-between mb-3">
                        <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center"
                            style={{ background: stat.bg, border: `1px solid ${stat.border}` }}
                        >
                            <stat.icon className="w-5 h-5" style={{ color: stat.color }} />
                        </div>
                    </div>
                    <p
                        className="text-2xl font-bold mb-1 animate-count"
                        style={{ color: stat.color }}
                    >
                        {stat.value}
                    </p>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                        {stat.label}
                    </p>
                </div>
            ))}
        </div>
    );
}
