"use client";

import React from "react";
import { CloudSun, Thermometer, Droplets, Wind } from "lucide-react";
import { WeatherData, MacroData } from "@/lib/api";

interface WeatherPanelProps {
    weather: WeatherData | null;
    macroData: MacroData[];
}

export default function WeatherPanel({ weather, macroData }: WeatherPanelProps) {
    return (
        <div className="glass-card p-6 animate-fade-in-up delay-400" style={{ opacity: 0, animationFillMode: "forwards" }}>
            {/* Weather Section */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-4">
                    <CloudSun className="w-5 h-5" style={{ color: "var(--accent-amber)" }} />
                    <h3 className="text-lg font-semibold">Cuaca</h3>
                </div>

                {weather ? (
                    <div>
                        <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
                            {weather.region || "Indonesia"} •{" "}
                            {new Date(weather.date).toLocaleDateString("id-ID", {
                                weekday: "long",
                                day: "numeric",
                                month: "long",
                            })}
                        </p>

                        {weather.weather_desc && (
                            <p className="text-sm font-medium mb-4" style={{ color: "var(--text-secondary)" }}>
                                {weather.weather_desc}
                            </p>
                        )}
                        {weather.temperature !== null ? (
                            <div className="grid grid-cols-3 gap-3">
                                <div className="p-3 rounded-xl text-center" style={{ background: "rgba(239, 68, 68, 0.05)" }}>
                                    <Thermometer className="w-4 h-4 mx-auto mb-1" style={{ color: "#f87171" }} />
                                    <p className="text-lg font-bold" style={{ color: "#f87171" }}>
                                        {weather.temperature}°
                                    </p>
                                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>Suhu</p>
                                </div>

                                <div className="p-3 rounded-xl text-center" style={{ background: "rgba(6, 182, 212, 0.05)" }}>
                                    <Droplets className="w-4 h-4 mx-auto mb-1" style={{ color: "#22d3ee" }} />
                                    <p className="text-lg font-bold" style={{ color: "#22d3ee" }}>
                                        {weather.humidity !== null ? `${weather.humidity}%` : "-"}
                                    </p>
                                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>Kelembapan</p>
                                </div>

                                <div className="p-3 rounded-xl text-center" style={{ background: "rgba(139, 92, 246, 0.05)" }}>
                                    <Wind className="w-4 h-4 mx-auto mb-1" style={{ color: "#a78bfa" }} />
                                    <p className="text-lg font-bold" style={{ color: "#a78bfa" }}>
                                        {weather.wind_speed !== null ? `${weather.wind_speed}` : "-"}
                                    </p>
                                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>km/jam</p>
                                </div>
                            </div>
                        ) : (
                            <div className="p-4 rounded-xl" style={{ background: "rgba(245, 158, 11, 0.05)", borderLeft: "4px solid var(--accent-amber)" }}>
                                <p className="text-xs" style={{ color: "var(--accent-amber)" }}>
                                    Peringatan Cuaca (Nowcast)
                                </p>
                            </div>
                        )}
                    </div>
                ) : (
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                        Belum ada data cuaca.
                    </p>
                )}
            </div>

            {/* Macro Economics */}
            <div>
                <h4 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
                    Indikator Ekonomi
                </h4>
                {macroData.length > 0 ? (
                    <div className="space-y-2">
                        {macroData.slice(0, 3).map((m, i) => (
                            <div
                                key={m.id || i}
                                className="flex items-center justify-between px-3 py-2 rounded-lg"
                                style={{ background: "rgba(255, 255, 255, 0.02)" }}
                            >
                                <span className="text-xs capitalize" style={{ color: "var(--text-secondary)" }}>
                                    {m.indicator}
                                    {m.period && (
                                        <span style={{ color: "var(--text-muted)" }}> ({m.period})</span>
                                    )}
                                </span>
                                <span className="text-xs font-bold" style={{ color: "var(--accent-emerald)" }}>
                                    {m.value.toFixed(2)}%
                                </span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                        Belum ada data makro ekonomi.
                    </p>
                )}
            </div>
        </div>
    );
}
