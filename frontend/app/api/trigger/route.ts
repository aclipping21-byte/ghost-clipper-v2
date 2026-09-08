import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { videoUrl } = await request.json();

    if (!videoUrl) {
      return NextResponse.json({ error: 'Video URL is required' }, { status: 400 });
    }

    const githubToken = process.env.GH_PAT;
    const repoOwner = process.env.GH_OWNER; // Your GitHub username
    const repoName = process.env.GH_REPO;   // Your repository name

    if (!githubToken || !repoOwner || !repoName) {
      return NextResponse.json({ error: 'GitHub credentials not configured on server' }, { status: 500 });
    }

    // Trigger the GitHub Actions workflow
    const ghResponse = await fetch(
      `https://api.github.com/repos/${repoOwner}/${repoName}/actions/workflows/process-video.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${githubToken}`,
          'Accept': 'application/vnd.github+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: { video_url: videoUrl }
        })
      }
    );

    if (!ghResponse.ok) {
      const errorText = await ghResponse.text();
      return NextResponse.json({ error: `GitHub API error: ${errorText}` }, { status: 500 });
    }

    return NextResponse.json({ success: true, message: 'Processing triggered successfully!' });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Internal server error' }, { status: 500 });
  }
}
