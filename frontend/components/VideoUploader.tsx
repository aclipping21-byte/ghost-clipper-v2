"use client";

import { useState } from "react";

export default function VideoUploader() {
  const [activeTab, setActiveTab] = useState<"transcribe" | "render">("transcribe");
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [clipsJson, setClipsJson] = useState<string>("");
  const [status, setStatus] = useState<string>("idle");
  const [message, setMessage] = useState<string>("");

  const handleTrigger = async (actionType: "transcribe" | "render") => {
    if (!videoUrl) return;
    if (actionType === "render" && !clipsJson) return;

    try {
      setStatus("processing");
      setMessage(
        actionType === "transcribe"
          ? "Starting Phase 1... Deepgram is transcribing your video."
          : "Starting Phase 2... MoviePy is rendering your viral clips."
      );

      const res = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: actionType,
          videoUrl,
          clipsJson: actionType === "render" ? clipsJson : undefined,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Failed to trigger process.");
      }

      setStatus("success");
      setMessage(
        actionType === "transcribe"
          ? "Phase 1 Triggered! Open your GitHub Actions summary in ~1 minute to copy your prompt."
          : "Phase 2 Triggered! Check your GitHub Actions dashboard in a few minutes for the completed zip file."
      );
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Something went wrong.");
    }
  };

  return (
    <div className="w-full max-w-2xl mt-8 p-6 border-2 border-dashed border-slate-700 rounded-2xl bg-slate-800/50 flex flex-col items-center">
      {/* Navigation Tabs */}
      <div className="flex gap-4 mb-6 w-full">
        <button
          onClick={() => { setActiveTab("transcribe"); setStatus("idle"); }}
          className={`flex-1 py-2 rounded-xl font-semibold transition-all ${
            activeTab === "transcribe" ? "bg-indigo-600 text-white" : "bg-slate-700 text-slate-300"
          }`}
        >
          1. Transcribe & Prompt
        </button>
        <button
          onClick={() => { setActiveTab("render"); setStatus("idle"); }}
          className={`flex-1 py-2 rounded-xl font-semibold transition-all ${
            activeTab === "render" ? "bg-indigo-600 text-white" : "bg-slate-700 text-slate-300"
          }`}
        >
          2. Render Clips
        </button>
      </div>

      {status === "processing" ? (
        <div className="flex flex-col items-center py-8 gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-indigo-400 font-medium text-center">{message}</p>
        </div>
      ) : (
        <div className="w-full flex flex-col gap-4">
          {activeTab === "transcribe" ? (
            <>
              <p className="text-slate-300 text-sm text-center">
                Step 1: Enter video link to generate the AI prompt in your GitHub Action Summary.
              </p>
              <input
                type="url"
                placeholder="[https://example.com/video.mp4](https://example.com/video.mp4)"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={() => handleTrigger("transcribe")}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all mt-2"
              >
                Generate Prompt
              </button>
            </>
          ) : (
            <>
              <p className="text-slate-300 text-sm text-center">
                Step 2: Re-enter video link & paste the AI JSON response to render.
              </p>
              <input
                type="url"
                placeholder="[https://example.com/video.mp4](https://example.com/video.mp4)"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <textarea
                rows={5}
                placeholder="Paste JSON output here..."
                value={clipsJson}
                onChange={(e) => setClipsJson(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-sm font-mono"
              />
              <button
                onClick={() => handleTrigger("render")}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all mt-2"
              >
                Start Rendering
              </button>
            </>
          )}

          {status === "success" && (
            <p className="mt-2 text-green-400 text-sm font-medium text-center">{message}</p>
          )}
          {status === "error" && (
            <p className="mt-2 text-red-400 text-sm font-medium text-center">{message}</p>
          )}
        </div>
      )}
    </div>
  );
      }
