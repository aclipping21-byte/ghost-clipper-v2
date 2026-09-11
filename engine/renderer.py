import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, TextClip
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from transcription import get_word_timestamps

def render_clip(video_path, clip_data, output_path):
    start_time = float(clip_data.get("start_time", 0))
    end_time = float(clip_data.get("end_time", 0))
    audio_enhance = clip_data.get("audio_enhance", False)
    cap_style = clip_data.get("caption_style", {})
    text_case = cap_style.get("case", "none") # AI can request "uppercase" or "lowercase"

    video = VideoFileClip(video_path)
    if end_time > video.duration:
        end_time = video.duration
    sub_clip = video.subclip(start_time, end_time)

    if audio_enhance:
        sub_clip = sub_clip.fx(afx.audio_normalize)

    # 1. Background Blur (9:16 vertical formatting)
    TARGET_W, TARGET_H = 1080, 1920
    bg_clip = sub_clip.resize(height=TARGET_H)
    bg_clip = bg_clip.crop(x_center=bg_clip.w/2, y_center=bg_clip.h/2, width=TARGET_W, height=TARGET_H)
    bg_clip = bg_clip.fx(vfx.colorx, 0.3) 

    fg_clip = sub_clip.resize(width=TARGET_W)
    fg_clip = fg_clip.set_position("center")

    layers = [bg_clip, fg_clip]

    # 2. Extract Subclip Audio & Get Exact Timestamps
    temp_audio_path = f"workspace/temp_audio.wav"
    sub_clip.audio.write_audiofile(temp_audio_path, logger=None)
    
    print("Fetching exact word timestamps from Deepgram...")
    words_data = get_word_timestamps(temp_audio_path)

    # 3. Smart Word Chunker (Groups 1-3 words dynamically)
    chunks = []
    current_chunk = []
    current_start = 0

    for i, w_info in enumerate(words_data):
        if not current_chunk:
            current_start = w_info['start']
        
        current_chunk.append(w_info['word'])
        
        is_last = (i == len(words_data) - 1)
        big_gap = False
        if not is_last:
            if words_data[i+1]['start'] - w_info['end'] > 0.4:
                big_gap = True
                
        if len(current_chunk) >= 3 or is_last or big_gap:
            chunks.append({
                'text': " ".join(current_chunk),
                'start': current_start,
                'end': w_info['end']
            })
            current_chunk = []

    # 4. Draw High-Quality "Always-On" Captions
    # Positioned slightly below center, exactly like the reference images
    Y_POS = TARGET_H * 0.55 
    
    for chunk in chunks:
        txt = chunk['text']
        if text_case == "uppercase":
            txt = txt.upper()
        elif text_case == "lowercase":
            txt = txt.lower()

        # Dual-Layer Shadow Technique (Bulletproof Drop Shadow)
        # 1. Draw the Black Shadow slightly lower and to the right
        shadow_clip = TextClip(txt, fontsize=90, color='black', font="DejaVu-Sans-Bold", method='caption', size=(TARGET_W * 0.85, None), align='center')
        shadow_clip = shadow_clip.set_position(('center', Y_POS + 5)).set_start(chunk['start']).set_end(chunk['end'])
        
        # 2. Draw the White Text on top
        txt_clip = TextClip(txt, fontsize=90, color='white', font="DejaVu-Sans-Bold", method='caption', size=(TARGET_W * 0.85, None), align='center')
        txt_clip = txt_clip.set_position(('center', Y_POS)).set_start(chunk['start']).set_end(chunk['end'])
        
        layers.append(shadow_clip)
        layers.append(txt_clip)

    # 5. Composite and Render
    final_video = CompositeVideoClip(layers, size=(TARGET_W, TARGET_H)).set_duration(sub_clip.duration)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30, preset="fast", logger=None)

    sub_clip.close()
    video.close()
    final_video.close()
