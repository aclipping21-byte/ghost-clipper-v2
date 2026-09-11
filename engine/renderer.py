import os
from moviepy.editor import VideoFileClip

def render_clip(video_path, clip_data, output_path):
    """
    Extracts a subclip from the source video based on start_time and end_time,
    and exports it as an mp4 file.
    """
    start_time = float(clip_data.get("start_time", 0))
    end_time = float(clip_data.get("end_time", 0))

    # Load source video
    video = VideoFileClip(video_path)

    # Validate duration bounds
    if end_time > video.duration:
        end_time = video.duration
    if start_time < 0 or start_time >= end_time:
        start_time = 0

    # Cut the clip
    sub_clip = video.subclip(start_time, end_time)

    # Render out the clip file
    sub_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    # Close file handles to release memory on the runner
    sub_clip.close()
    video.close()
