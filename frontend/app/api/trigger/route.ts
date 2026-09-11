import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { action, videoUrl, clipsJson } = body;

    const token = process.env.GH_PAT;
    const owner = process.env.GH_OWNER;
    const repo = process.env.GH_REPO;

    if (!token || !owner || !repo) {
      return NextResponse.json({ error: "Missing GitHub credentials in Netlify settings." }, { status: 500 });
    }

    const eventType = action === "render" ? "phase2_render" : "phase1_transcribe";
    const clientPayload = action === "render" ? { videoUrl, clipsJson } : { videoUrl };

    const res = await fetch(`[https://api.github.com/repos/$](https://api.github.com/repos/$){owner}/${repo}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event_type: eventType,
        client_payload: clientPayload,
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      return NextResponse.json({ error: `GitHub API error: ${errText}` }, { status: res.status });
    }

    return NextResponse.json({ success: true });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || "Failed to trigger process." }, { status: 500 });
  }
}
