import { NextRequest, NextResponse } from "next/server";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;
        const res = await fetch(`https://wilayah.web.id/api/regencies/${id}`, {
            headers: {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            cache: "no-store",
        });

        if (!res.ok) {
            throw new Error(`Wilayah API responded with status: ${res.status}`);
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error: any) {
        console.error(`Error fetching regencies for ${request.url}:`, error.message);
        return NextResponse.json(
            { status: "error", message: error.message, data: [] },
            { status: 500 }
        );
    }
}
