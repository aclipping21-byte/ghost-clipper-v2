"use client";

import { useState } from "react";

export default function VideoUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("idle"); // idle, uploading, processing, success, error
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
      setMessage("Uploading video to secure temporary storage...");

      // 1. Get the best server from GoFile (Free tier API)
      const serverRes = await fetch("https://api.gofile.io/servers", { method: "GET" });
      const serverData = await serverRes.json();
      
      if (serverData.status !== "ok") {
        throw new Error("Could not connect to storage provider.");
      }
      
      const serverName = serverData.data.servers[0].name;

      // 2. Upload the file to that specific GoFile server
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`https://${serverName}.gofile.io/contents/uploadfile`, {
        method: "POST",
        body: formData,
      });
      
      const uploadData = await uploadRes.json();

      if (uploadData.status !== "ok") {
        throw new Error("Failed to upload video.");
      }

      const downloadUrl = uploadData.data.downloadPage;

      // 3. Trigger GitHub Actions via our Next.js API
      setStatus("processing");
      setMessage("Upload complete! Sending to AI Director in GitHub Actions...");

      const triggerRes = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoUrl: downloadUrl }),
      });

      if (!triggerRes.ok) {
        const errorData = await triggerRes.json();
        throw new Error(errorData.error || "Failed to trigger pipeline.");
      }

      setStatus("success");
      setMessage("Success! The AI Director is now editing your clips. Check your GitHub Actions dashboard in a few minutes.");

    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Something went wrong.");
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
