import os
import subprocess
from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

class VideoRenderer:
    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_ffmpeg(self, cmd):
        """Helper function to run raw FFmpeg commands."""
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"FFmpeg Error: {result.stderr}")
            raise RuntimeError("FFmpeg processing failed.")

    def isolate_raw_segment(self, source_path, start_time, end_time, clip_id):
        """
        Fast-cuts a segment from the main video using stream copy.
        Takes 1 second and consumes almost zero RAM.
        """
        duration = end_time - start_time
        temp_cut_path = self.output_dir / f"temp_raw_{clip_id}.mp4"

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(source_path),
            "-t", str(duration),
            "-c:v", "copy", "-c:a", "copy",
            str(temp_cut_path)
        ]
        self.run_ffmpeg(cmd)
        return temp_cut_path

    def render_clip(self, source_path, clip_data, output_filename):
        clip_id = clip_data.get("clip_id", 1)
        start_time = clip_data.get("start_time", 0)
        end_time = clip_data.get("end_time", 10)

        print(f"Rendering Clip #{clip_id} ({start_time}s to {end_time}s)...")

        # Step 1: Instant stream-copy cut
        temp_raw = self.isolate_raw_segment(source_path, start_time, end_time, clip_id)

        target_w, target_h = 1080, 1920  # standard 9:16 vertical video

        # Step 2: Load only the short clip into MoviePy
        base_clip = VideoFileClip(str(temp_raw))
        layers = []

        # Formatting: 9:16 vertical setup with black background
        formatted_clip = base_clip.resize(width=target_w).set_position("center")
        bg = ColorClip(size=(target_w, target_h), color=(0, 0, 0)).set_duration(base_clip.duration)
        layers.extend([bg, formatted_clip])

        # Step 3: Apply Gemini's requested creative edits
        for edit in clip_data.get("edits", []):
            edit_type = edit.get("type")
            
            if edit_type in ["hook_text", "animated_card"]:
                text_content = edit.get("text", "")
                text_start = edit.get("start", 0)
                text_end = edit.get("end", base_clip.duration)

                # Overlay hook text on screen
                txt_clip = TextClip(
                    text_content,
                    fontsize=75,
                    color="white",
                    font="Impact",
                    stroke_color="black",
                    stroke_width=4,
                    method="caption",
                    size=(int(target_w * 0.85), None)
                )
                txt_clip = txt_clip.set_position("center").set_start(text_start).set_end(text_end)
                layers.append(txt_clip)

            elif edit_type == "flash":
                flash_color = (255, 0, 0) if edit.get("color") == "red" else (255, 255, 255)
                flash_time = edit.get("time", 0)

                # Create a quick 0.15s color flash
                flash = ColorClip(size=(target_w, target_h), color=flash_color)
                flash = flash.set_duration(0.15).set_start(flash_time).set_opacity(0.4)
                layers.append(flash)

        # Step 4: Composite layers and export file
        final_video = CompositeVideoClip(layers, size=(target_w, target_h))
        final_path = self.output_dir / output_filename

        final_video.write_videofile(
            str(final_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",  # Speeds up export time significantly
            threads=2,          # Fits GitHub Actions CPU capacity
            logger=None
        )

        # Cleanup temporary files
        base_clip.close()
        final_video.close()
        if temp_raw.exists():
            os.remove(temp_raw)

        print(f"Finished rendering: {final_path}")
        return final_path

if __name__ == "__main__":
    pass
