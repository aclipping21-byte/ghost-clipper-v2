"use client";

import { useState } from "react";

export default function VideoUploader() {
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [status, setStatus] = useState<string>("idle"); // idle, processing, success, error
  const [message, setMessage] = useState<string>("");

  const startProcess = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!videoUrl) return;

    try {
      setStatus("processing");
      setMessage("Sending video link to the AI Director in GitHub Actions...");

      const triggerRes = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoUrl: videoUrl }),
      });

      if (!triggerRes.ok) {
        const errorData = await triggerRes.json();
        throw new Error(errorData.error || "Failed to trigger pipeline.");
      }

      setStatus("success");
      setMessage("Success! The AI Director is now processing your video. Check your GitHub Actions dashboard!");

    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Something went wrong. Check your GitHub credentials in Netlify.");
    }
  };

  return (
    <div className="w-full max-w-2xl mt-8 p-8 border-2 border-dashed border-slate-700 rounded-2xl bg-slate-800/50 flex flex-col items-center justify-center min-h-[300px]">
      
      {status === "idle" || status === "error" ? (
        <form onSubmit={startProcess} className="w-full flex flex-col items-center gap-4">
          <p className="text-slate-300 font-medium text-center mb-2">
            Paste a direct public link to your video (Google Drive, Dropbox, etc.)
          </p>
          
          <input
            type="url"
            placeholder="https://example.com/my-video.mp4"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          
          <button
            type="submit"
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full font-bold transition-all mt-4"
          >
            Start AI Extraction
          </button>

          {status === "error" && (
            <p className="mt-4 text-red-400 font-medium text-center">{message}</p>
          )}
        </form>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-indigo-400 font-medium text-center">{message}</p>
        </div>
      )}

    </div>
  );
}
