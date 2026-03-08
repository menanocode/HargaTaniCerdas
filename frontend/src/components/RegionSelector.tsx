"use client";

import React, { useState, useEffect } from "react";
import { MapPin, Search, Loader2 } from "lucide-react";

interface RegionSelectorProps {
    kodeProvinsi: string;
    kodeKabKota: string;
    tanggal: string;
    tanggalPembanding: string;
    onApply: (prov: string, kab: string, tgl: string, tglP: string) => void;
    isLoading?: boolean;
}

export default function RegionSelector({
    kodeProvinsi,
    kodeKabKota,
    tanggal,
    tanggalPembanding,
    onApply,
    isLoading = false,
}: RegionSelectorProps) {
    const [prov, setProv] = useState(kodeProvinsi);
    const [kab, setKab] = useState(kodeKabKota);
    const [tgl, setTgl] = useState(tanggal);
    const [tglP, setTglP] = useState(tanggalPembanding);

    const [provinces, setProvinces] = useState<{ code: string; name: string }[]>([]);
    const [regencies, setRegencies] = useState<{ code: string; name: string }[]>([]);
    const [loadingProv, setLoadingProv] = useState(false);
    const [loadingKab, setLoadingKab] = useState(false);

    // Fetch provinces on mount
    useEffect(() => {
        let isMounted = true;
        const fetchProvinces = async () => {
            setLoadingProv(true);
            try {
                const res = await fetch("/api/wilayah/provinces");
                const data = await res.json();
                if (isMounted && data.status === "success" && data.data) {
                    setProvinces(data.data);
                }
            } catch (err) {
                console.error("Failed to fetch provinces:", err);
            } finally {
                if (isMounted) setLoadingProv(false);
            }
        };
        fetchProvinces();
        return () => { isMounted = false; };
    }, []);

    // Fetch regencies when prov changes
    useEffect(() => {
        if (!prov) {
            setRegencies([]);
            return;
        }
        let isMounted = true;
        const fetchRegencies = async () => {
            setLoadingKab(true);
            try {
                const res = await fetch(`/api/wilayah/regencies/${prov}`);
                const data = await res.json();
                if (isMounted && data.status === "success" && data.data) {
                    setRegencies(data.data);
                }
            } catch (err) {
                console.error("Failed to fetch regencies:", err);
            } finally {
                if (isMounted) setLoadingKab(false);
            }
        };
        fetchRegencies();
        return () => { isMounted = false; };
    }, [prov]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onApply(prov, kab, tgl, tglP);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="flex flex-col sm:flex-row items-center gap-3 p-3 rounded-xl"
            style={{
                background: "var(--card-bg)",
                border: "1px solid var(--border-subtle)",
            }}
        >
            <div className="flex items-center gap-2">
                <MapPin size={18} style={{ color: "var(--accent-primary)" }} />
                <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                    Wilayah SP2KP:
                </span>
            </div>

            <div className="flex items-center gap-2">
                <div className="relative">
                    <select
                        value={prov}
                        onChange={(e) => {
                            setProv(e.target.value);
                            setKab(""); // reset kab on prov change
                        }}
                        disabled={loadingProv}
                        className="w-40 px-3 py-1.5 text-sm rounded-lg outline-none transition-colors appearance-none"
                        style={{
                            background: "var(--bg-primary)",
                            border: "1px solid var(--border-subtle)",
                            color: "var(--text-primary)",
                        }}
                    >
                        <option value="">Pilih Provinsi</option>
                        {provinces.map((p) => (
                            <option key={p.code} value={p.code}>
                                {p.name}
                            </option>
                        ))}
                    </select>
                    {loadingProv && (
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                            <Loader2 size={14} className="animate-spin" />
                        </div>
                    )}
                </div>

                <div className="relative">
                    <select
                        value={kab}
                        onChange={(e) => setKab(e.target.value)}
                        disabled={!prov || loadingKab}
                        className="w-48 px-3 py-1.5 text-sm rounded-lg outline-none transition-colors appearance-none disabled:opacity-50"
                        style={{
                            background: "var(--bg-primary)",
                            border: "1px solid var(--border-subtle)",
                            color: "var(--text-primary)",
                        }}
                    >
                        <option value="">Pilih Kab/Kota</option>
                        {regencies.map((r) => (
                            <option key={r.code} value={r.code}>
                                {r.name}
                            </option>
                        ))}
                    </select>
                    {loadingKab && (
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                            <Loader2 size={14} className="animate-spin" />
                        </div>
                    )}
                </div>

                {/* Date Inputs */}
                <span className="text-gray-400 text-sm ml-2 mr-1">Tgl:</span>
                <input
                    type="date"
                    value={tgl}
                    onChange={(e) => setTgl(e.target.value)}
                    className="w-36 px-3 py-1.5 text-sm rounded-lg outline-none transition-colors"
                    style={{
                        background: "var(--bg-primary)",
                        border: "1px solid var(--border-subtle)",
                        color: "var(--text-primary)",
                        colorScheme: "dark"
                    }}
                    title="Tanggal Utama"
                />

                <span className="text-gray-400 text-sm mx-1">Vs:</span>
                <input
                    type="date"
                    value={tglP}
                    onChange={(e) => setTglP(e.target.value)}
                    className="w-36 px-3 py-1.5 text-sm rounded-lg outline-none transition-colors"
                    style={{
                        background: "var(--bg-primary)",
                        border: "1px solid var(--border-subtle)",
                        color: "var(--text-primary)",
                        colorScheme: "dark"
                    }}
                    title="Tanggal Pembanding"
                />

                <button
                    type="submit"
                    disabled={isLoading || !prov || !kab}
                    className="flex items-center justify-center p-2 rounded-lg transition-colors hover:opacity-90 disabled:opacity-50 ml-1"
                    style={{
                        background: "var(--accent-primary)",
                        color: "white",
                    }}
                    title="Terapkan Wilayah"
                >
                    <Search size={16} />
                </button>
            </div>
        </form>
    );
}
