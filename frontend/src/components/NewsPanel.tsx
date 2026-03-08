"use client";

import React from "react";
import { Newspaper, ExternalLink } from "lucide-react";
import { NewsData } from "@/lib/api";

interface NewsPanelProps {
    news: NewsData[];
}

export default function NewsPanel({ news }: NewsPanelProps) {
    return (
        <div className="glass-card p-6 animate-fade-in-up delay-300" style={{ opacity: 0, animationFillMode: "forwards" }}>
            <div className="flex items-center gap-2 mb-5">
                <Newspaper className="w-5 h-5" style={{ color: "var(--accent-amber)" }} />
                <h3 className="text-lg font-semibold">Berita Ekonomi</h3>
                <span className="text-xs px-2 py-0.5 rounded-lg ml-auto" style={{ background: "rgba(245, 158, 11, 0.1)", color: "var(--accent-amber)" }}>
                    {news.length} berita
                </span>
            </div>

            {news.length === 0 ? (
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    Belum ada berita. Klik Refresh untuk mengambil data.
                </p>
            ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                    {news.map((item, i) => (
                        <div
                            key={item.id || i}
                            className="p-3 rounded-xl transition-all hover:translate-x-1"
                            style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border-subtle)" }}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                    {item.url ? (
                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-sm font-medium hover:underline line-clamp-2"
                                            style={{ color: "var(--text-primary)" }}
                                        >
                                            {item.title}
                                        </a>
                                    ) : (
                                        <p className="text-sm font-medium line-clamp-2" style={{ color: "var(--text-primary)" }}>
                                            {item.title}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                                            {new Date(item.date).toLocaleDateString("id-ID", {
                                                day: "numeric",
                                                month: "short",
                                                year: "numeric",
                                            })}
                                        </span>
                                        {item.sentiment_label && (
                                            <span
                                                className={`text-xs px-2 py-0.5 rounded-full sentiment-${item.sentiment_label}`}
                                            >
                                                {item.sentiment_label}
                                                {item.sentiment_score !== null && (
                                                    <> ({item.sentiment_score > 0 ? "+" : ""}{item.sentiment_score.toFixed(2)})</>
                                                )}
                                            </span>
                                        )}
                                        {item.related_commodity && (
                                            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "rgba(6, 182, 212, 0.1)", color: "var(--accent-cyan)" }}>
                                                {item.related_commodity}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                {item.url && (
                                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0">
                                        <ExternalLink className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
