"use client";

import { useState } from "react";

export default function VideoUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [message, setMessage] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus("idle");
      setMessage("");
    }
  };

  const startProcess = async () => {
    if (!file) return;

    try {
      setStatus("uploading");
      setMessage("Uploading large video... This may take a few minutes depending on your connection.");

      // 1. Upload the file to storage.to (Supports up to 25GB, no timeout on mobile)
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch("https://storage.to/api/upload/init", {
        method: "POST",
        body: formData,
      });
      
      const uploadData = await uploadRes.json();

      if (!uploadRes.ok || !uploadData.url) {
        throw new Error("Failed to upload video to storage provider.");
      }

      // Storage.to provides a view page link. We append ?download=1 or parse it 
      // to ensure GitHub Actions gets the raw video bytes.
      // Usually it returns something like: https://storage.to/v/abc12345
      // To get the raw file, their API allows adding /raw to the path
      let rawDownloadUrl = uploadData.url;
      if (rawDownloadUrl.includes("/v/")) {
          rawDownloadUrl = rawDownloadUrl.replace("/v/", "/raw/");
      }

      // 2. Trigger GitHub Actions via our Next.js API
      setStatus("processing");
      setMessage("Upload complete! Sending to AI Director in GitHub Actions...");

      const triggerRes = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoUrl: rawDownloadUrl }),
      });

      if (!triggerRes.ok) {
        const errorData = await triggerRes.json();
        throw new Error(errorData.error || "Failed to trigger pipeline.");
      }

      setStatus("success");
      setMessage("Success! The AI Director is now editing your clips. Check your GitHub Actions dashboard.");

    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Something went wrong. Please check your connection.");
    }
  };

  return (
    <div className="w-full max-w-2xl mt-8 p-8 border-2 border-dashed border-slate-700 rounded-2xl bg-slate-800/50 flex flex-col items-center justify-center min-h-[300px]">
      
      {status === "idle" || status === "error" ? (
        <>
          <input
            type="file"
            accept="video/mp4,video/mov,video/quicktime"
            onChange={handleFileChange}
            className="block w-full text-sm text-slate-400
              file:mr-4 file:py-3 file:px-6
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-indigo-600 file:text-white
              hover:file:bg-indigo-500 cursor-pointer mb-6"
          />
          
          {file && (
            <button
              onClick={startProcess}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full font-bold transition-all"
            >
              Start AI Extraction
            </button>
          )}

          {status === "error" && (
            <p className="mt-4 text-red-400 font-medium text-center">{message}</p>
          )}
        </>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-indigo-400 font-medium text-center">{message}</p>
        </div>
      )}

    </div>
  );
}
