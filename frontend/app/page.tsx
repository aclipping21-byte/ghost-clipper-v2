export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 md:p-24">
      <div className="z-10 max-w-5xl w-full flex flex-col items-center gap-6">
        
        <h1 className="text-5xl md:text-7xl font-bold text-center tracking-tight">
          Ghost Clipper <span className="text-indigo-500">V2</span>
        </h1>
        
        <p className="text-center text-slate-400 text-lg md:text-xl max-w-2xl">
          The $0 AI Director. Upload a long video, and let the system automatically extract and edit highly-viral short clips.
        </p>
        
        {/* We will build and place our VideoUploader component here in the next step */}
        <div className="w-full max-w-2xl mt-8 p-12 border-2 border-dashed border-slate-700 rounded-2xl bg-slate-800/30 flex items-center justify-center min-h-[300px]">
          <p className="text-slate-500 font-medium">Video uploader coming in the next step...</p>
        </div>

      </div>
    </main>
  )
}
