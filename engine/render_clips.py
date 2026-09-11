import os
import sys
import json
from download import download_video
from renderer import ClipRenderer

def main():
    video_url = os.environ.get("VIDEO_URL")
    raw_json = os.environ.get("CLIPS_JSON")

    if not video_url or not raw_json:
        print("Error: Missing VIDEO_URL or CLIPS_JSON environment variable.")
        sys.exit(1)

    # Clean leading/trailing whitespace FIRST
    raw_json = raw_json.strip()

    # Clean markdown wrapper if present
    if raw_json.startswith("```json"):
        raw_json = raw_json[7:]
    elif raw_json.startswith("```"):
        raw_json = raw_json[3:]
    if raw_json.endswith("```"):
        raw_json = raw_json[:-3]
        
    raw_json = raw_json.strip()

    try:
        parsed = json.loads(raw_json)
        clips = parsed.get("clips", [])
    except Exception as e:
        print(f"Failed to parse JSON input: {e}")
        sys.exit(1)

    if not clips:
        print("No clips found in the provided JSON.")
        sys.exit(1)

    os.makedirs("workspace", exist_ok=True)
    source_video_path = "workspace/input_video.mp4"

    print(f"Downloading video from: {video_url}")
    download_video(video_url, source_video_path)

    renderer = ClipRenderer()
    output_dir = "workspace/output"
    os.makedirs(output_dir, exist_ok=True)

    for i, clip in enumerate(clips):
        output_filename = os.path.join(output_dir, f"clip_{i+1}.mp4")
        print(f"Rendering Clip #{i+1} ({clip['start_time']}s to {clip['end_time']}s)...")
        renderer.render_clip(source_video_path, clip, output_filename)

    print("All clips rendered successfully!")

if __name__ == "__main__":
    main()
