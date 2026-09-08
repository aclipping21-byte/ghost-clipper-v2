import os
import sys
import subprocess
import requests
from pathlib import Path

from transcription import get_transcript
from director import analyze_transcript_and_plan_edits
from renderer import VideoRenderer

def download_video(url, output_path):
    print(f"Downloading video from: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print("Download complete!")

def extract_audio(video_path, audio_path):
    print("Extracting audio from video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        str(audio_path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"FFmpeg Audio Extraction Error: {result.stderr}")
        raise RuntimeError("Audio extraction failed.")
    print("Audio extraction complete!")

def main():
    video_url = os.environ.get("VIDEO_URL")
    
    workspace_dir = Path("./workspace")
    output_dir = Path("./output")
    workspace_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    source_video_path = workspace_dir / "input_video.mp4"
    audio_path = workspace_dir / "input_audio.mp3"

    # Step 1: Obtain video file
    if video_url:
        download_video(video_url, source_video_path)
    elif len(sys.argv) > 1:
        source_video_path = Path(sys.argv[1])
    else:
        raise ValueError("No video provided! Set VIDEO_URL environment variable or pass a local video path.")

    # Step 2: Extract Audio
    extract_audio(source_video_path, audio_path)

    # Step 3: Transcribe with Deepgram
    transcript = get_transcript(audio_path)
    if not transcript:
        print("No transcript produced. Exiting.")
        return

    # Step 4: Analyze with Gemini Director
    edit_plan = analyze_transcript_and_plan_edits(transcript)

    # Step 5: Render Clips
    renderer = VideoRenderer(output_dir=output_dir)
    clips = edit_plan.get("clips", [])

    print(f"Starting rendering for {len(clips)} clip(s)...")
    for clip in clips:
        clip_id = clip.get("clip_id", 1)
        output_filename = f"ghost_clip_{clip_id}.mp4"
        renderer.render_clip(source_video_path, clip, output_filename)

    print("All processing complete! Clips ready in output directory.")

if __name__ == "__main__":
    main()
