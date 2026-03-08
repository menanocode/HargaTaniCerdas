"use client";

import React from "react";
import {
    BarChart3,
    Wheat,
    RefreshCw,
} from "lucide-react";

interface NavbarProps {
    onRefresh: () => void;
    isLoading: boolean;
}

export default function Navbar({ onRefresh, isLoading }: NavbarProps) {
    return (
        <nav className="sticky top-0 z-50 glass-card rounded-none border-x-0 border-t-0"
            style={{ borderRadius: 0 }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center"
                            style={{ background: "var(--gradient-primary)" }}
                        >
                            <Wheat className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold gradient-text">
                                HargaTaniCerdas
                            </h1>
                            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                                Prediksi Harga Bahan Pokok
                            </p>
                        </div>
                    </div>

                    {/* Right section */}
                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg"
                            style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
                            <BarChart3 className="w-4 h-4" style={{ color: "var(--accent-emerald)" }} />
                            <span className="text-xs font-medium" style={{ color: "var(--accent-emerald)" }}>
                                AI Powered
                            </span>
                        </div>
                        <button
                            onClick={onRefresh}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-105 disabled:opacity-50"
                            style={{
                                background: "var(--gradient-primary)",
                                color: "white",
                                boxShadow: "0 4px 15px rgba(16, 185, 129, 0.3)",
                            }}
                        >
                            <RefreshCw
                                className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
                            />
                            {isLoading ? "Memuat..." : "Refresh Data"}
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
