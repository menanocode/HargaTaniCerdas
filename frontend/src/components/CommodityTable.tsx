"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { CommoditySummary, formatCurrency, formatPercent } from "@/lib/api";

interface CommodityTableProps {
    commodities: CommoditySummary[];
    selected: string;
    onSelect: (commodity: string) => void;
}

export default function CommodityTable({
    commodities,
    selected,
    onSelect,
}: CommodityTableProps) {
    return (
        <div className="glass-card p-6 animate-fade-in-up delay-200" style={{ opacity: 0, animationFillMode: "forwards" }}>
            <h3 className="text-lg font-semibold mb-4">Daftar Komoditas</h3>

            {commodities.length === 0 ? (
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    Belum ada data komoditas.
                </p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                                <th className="text-left py-3 px-2 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                                    Komoditas
                                </th>
                                <th className="text-right py-3 px-2 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                                    Harga
                                </th>
                                <th className="text-right py-3 px-2 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                                    Perubahan
                                </th>
                                <th className="text-right py-3 px-2 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                                    Tren
                                </th>
                                <th className="text-right py-3 px-2 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                                    Prediksi
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {commodities.map((c, i) => {
                                const isSelected = c.commodity === selected;
                                const changeColor =
                                    c.change_percent !== null && c.change_percent > 0
                                        ? "var(--accent-red)"
                                        : c.change_percent !== null && c.change_percent < 0
                                            ? "var(--accent-emerald)"
                                            : "var(--accent-amber)";

                                return (
                                    <tr
                                        key={c.commodity}
                                        onClick={() => onSelect(c.commodity)}
                                        className="cursor-pointer transition-all"
                                        style={{
                                            borderBottom: "1px solid var(--border-subtle)",
                                            background: isSelected
                                                ? "rgba(16, 185, 129, 0.08)"
                                                : "transparent",
                                        }}
                                        onMouseEnter={(e) => {
                                            if (!isSelected)
                                                e.currentTarget.style.background = "rgba(255,255,255,0.02)";
                                        }}
                                        onMouseLeave={(e) => {
                                            if (!isSelected)
                                                e.currentTarget.style.background = "transparent";
                                        }}
                                    >
                                        <td className="py-3 px-2">
                                            <div className="flex items-center gap-2">
                                                {isSelected && (
                                                    <div
                                                        className="w-1.5 h-1.5 rounded-full"
                                                        style={{ background: "var(--accent-emerald)" }}
                                                    />
                                                )}
                                                <span className="font-medium capitalize">
                                                    {c.commodity}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-2 text-right font-semibold">
                                            {c.latest_price ? formatCurrency(c.latest_price) : "-"}
                                        </td>
                                        <td className="py-3 px-2 text-right">
                                            <span style={{ color: changeColor }}>
                                                {formatPercent(c.change_percent)}
                                            </span>
                                        </td>
                                        <td className="py-3 px-2 text-right">
                                            {c.trend ? (
                                                <span
                                                    className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${c.trend === "naik"
                                                            ? "badge-naik"
                                                            : c.trend === "turun"
                                                                ? "badge-turun"
                                                                : "badge-stabil"
                                                        }`}
                                                >
                                                    {c.trend === "naik" ? (
                                                        <TrendingUp className="w-3 h-3" />
                                                    ) : c.trend === "turun" ? (
                                                        <TrendingDown className="w-3 h-3" />
                                                    ) : (
                                                        <Minus className="w-3 h-3" />
                                                    )}
                                                    {c.trend}
                                                </span>
                                            ) : (
                                                <span style={{ color: "var(--text-muted)" }}>-</span>
                                            )}
                                        </td>
                                        <td className="py-3 px-2 text-right">
                                            <span style={{ color: "var(--accent-cyan)" }}>
                                                {c.predicted_price
                                                    ? formatCurrency(c.predicted_price)
                                                    : "-"}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
