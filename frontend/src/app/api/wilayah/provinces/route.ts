import { NextResponse } from "next/server";

export async function GET() {
    try {
        const res = await fetch("https://wilayah.web.id/api/provinces", {
            headers: {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            // Disable caching for this API route to ensure fresh data
            cache: "no-store",
        });

        if (!res.ok) {
            throw new Error(`Wilayah API responded with status: ${res.status}`);
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error: any) {
        console.error("Error fetching provinces:", error.message);
        return NextResponse.json(
            { status: "error", message: error.message, data: [] },
            { status: 500 }
        );
    }
}
