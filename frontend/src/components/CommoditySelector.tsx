"use client";

import React from "react";
import { ChevronDown } from "lucide-react";

interface CommoditySelectorProps {
    commodities: string[];
    selected: string;
    onSelect: (commodity: string) => void;
}

export default function CommoditySelector({
    commodities,
    selected,
    onSelect,
}: CommoditySelectorProps) {
    return (
        <div className="relative">
            <select
                value={selected}
                onChange={(e) => onSelect(e.target.value)}
                className="appearance-none w-full px-4 py-2.5 pr-10 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 cursor-pointer transition-all duration-200"
                style={{
                    background: "var(--bg-card)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",

                }}
            >
                {commodities.map((c) => (
                    <option key={c} value={c} style={{ background: "var(--bg-secondary)" }}>
                        {c.charAt(0).toUpperCase() + c.slice(1)}
                    </option>
                ))}
            </select>
            <ChevronDown
                className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                style={{ color: "var(--text-muted)" }}
            />
        </div>
    );
}
