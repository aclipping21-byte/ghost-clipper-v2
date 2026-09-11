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

    prompt_text = f"""You are an expert AI video director for TikTok/Reels. Read the transcript below and identify 1 to 2 highly viral clips (15-60s). 
Your editing philosophy: Content and retention come first. Do not overuse effects. Use surgical edits to enhance retention.

You have access to these specific effects:
- "hook_text": Bold white text on a black screen for the first 3 seconds.
- "zooms": "zoom_in" (smooth push in) or "zoom_out".
- "flashes": "green_flash" or "red_flash" for emphasis.
- "cards": Pop-up text cards entering from outside frame (e.g., "WTF", "AGREED", "BULLSH*T").
- "caption_style": Font style ("standard", "impact", "minimal") and animation ("pop", "word_by_word", "color_highlight").
- "screen_mode": "white_screen" or "black_screen" with large text for dramatic pauses.

STRICT REQUIREMENT: Reply ONLY in valid JSON matching this exact structure:
{{
  "clips": [
    {{
      "start_time": 12.5,
      "end_time": 45.0,
      "title": "Insane hook title",
      "audio_enhance": true,
      "caption_style": {{
        "font": "impact",
        "animation": "color_highlight",
        "highlight_color": "yellow"
      }},
      "hook_text": "YOU'VE BEEN DOING THIS WRONG",
      "visual_effects": [
        {{"type": "zoom_in", "time": 15.0}},
        {{"type": "green_flash", "time": 22.5}},
        {{"type": "animated_card", "text": "BULLSH*T", "time": 28.0}},
        {{"type": "black_screen", "text": "Wait for it...", "start": 35.0, "end": 36.5}}
      ]
    }}
  ]
}}

Transcript with timestamps:
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
