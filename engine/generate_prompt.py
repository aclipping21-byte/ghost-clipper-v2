import os
import sys
import subprocess
from download import download_video
from transcription import get_transcript

def extract_audio(video_path, audio_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(res.stderr.decode('utf-8'))
        raise RuntimeError("Audio extraction failed.")

def main():
    video_url = os.environ.get("VIDEO_URL")
    if not video_url:
        print("Error: VIDEO_URL environment variable is missing.")
        sys.exit(1)

    os.makedirs("workspace", exist_ok=True)
    source_video_path = "workspace/input_video.mp4"
    audio_path = "workspace/input_audio.mp3"

    print(f"Downloading video from: {video_url}")
    download_video(video_url, source_video_path)

    print("Extracting audio from video...")
    extract_audio(source_video_path, audio_path)

    print("Starting Deepgram transcription...")
    transcript = get_transcript(audio_path)
    print("Transcription complete!\n")

    prompt_text = f"""You are an expert AI video director. Read this transcript and identify 1 to 3 viral short clips (15 to 60 seconds each).

STRICT REQUIREMENT: Reply ONLY in valid JSON matching this exact structure:
{{
  "clips": [
    {{
      "start_time": 12.5,
      "end_time": 45.0,
      "title": "Viral Moment Title"
    }}
  ]
}}

Transcript:
{transcript}"""

    print("=" * 40)
    print("PROMPT READY FOR AI:")
    print("=" * 40)

    # Post directly to GitHub Action Summary for easy mobile copying
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write("## 📋 Your AI Director Prompt (Copy This!)\n\n")
            f.write("```text\n")
            f.write(prompt_text)
            f.write("\n```\n")

if __name__ == "__main__":
    main()
