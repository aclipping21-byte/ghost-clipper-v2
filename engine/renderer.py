import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, TextClip
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx

def render_clip(video_path, clip_data, output_path):
    # 1. Parse Clip Data
    start_time = float(clip_data.get("start_time", 0))
    end_time = float(clip_data.get("end_time", 0))
    effects = clip_data.get("visual_effects", [])
    hook_text = clip_data.get("hook_text", None)
    audio_enhance = clip_data.get("audio_enhance", False)

    # 2. Load and Cut Source Video
    video = VideoFileClip(video_path)
    if end_time > video.duration:
        end_time = video.duration
    sub_clip = video.subclip(start_time, end_time)

    # 3. Audio Enhancement (Normalization)
    if audio_enhance:
        sub_clip = sub_clip.fx(afx.audio_normalize)

    # 4. Automatic 9:16 Vertical Formatting
    TARGET_W, TARGET_H = 1080, 1920
    
    # Create the background (scaled up and darkened)
    bg_clip = sub_clip.resize(height=TARGET_H)
    bg_clip = bg_clip.crop(x_center=bg_clip.w/2, y_center=bg_clip.h/2, width=TARGET_W, height=TARGET_H)
    bg_clip = bg_clip.fx(vfx.colorx, 0.3) # <-- FIX: Applied correctly using .fx()

    # Create the foreground (fit to width)
    fg_clip = sub_clip.resize(width=TARGET_W)
    fg_clip = fg_clip.set_position("center")

    layers = [bg_clip, fg_clip]

    # 5. Build Visual Effects Timeline
    for effect in effects:
        effect_type = effect.get("type")
        effect_time = float(effect.get("time", 0)) - start_time
        
        # Ensure effect isn't outside the clip timeline
        if effect_time < 0 or effect_time > sub_clip.duration:
            continue

        if effect_type == "green_flash":
            flash = ColorClip(size=(TARGET_W, TARGET_H), color=(0, 255, 0)).set_opacity(0.4).set_duration(0.15).set_start(effect_time)
            layers.append(flash)
            
        elif effect_type == "red_flash":
            flash = ColorClip(size=(TARGET_W, TARGET_H), color=(255, 0, 0)).set_opacity(0.4).set_duration(0.15).set_start(effect_time)
            layers.append(flash)
            
        elif effect_type == "animated_card":
            text = effect.get("text", "!")
            # FIX: Removed the unsupported 'padding' argument
            txt_clip = TextClip(text, fontsize=120, color='white', bg_color='red', font="DejaVu-Sans-Bold")
            txt_clip = txt_clip.set_position("center").set_start(effect_time).set_duration(1.5)
            layers.append(txt_clip)
            
        elif effect_type in ["black_screen", "white_screen"]:
            eff_start = float(effect.get("start", start_time)) - start_time
            eff_end = float(effect.get("end", start_time + 1)) - start_time
            bg_color = (0,0,0) if effect_type == "black_screen" else (255,255,255)
            txt_color = 'white' if effect_type == "black_screen" else 'black'
            
            screen = ColorClip(size=(TARGET_W, TARGET_H), color=bg_color).set_start(eff_start).set_end(eff_end)
            text_overlay = TextClip(effect.get("text", ""), fontsize=100, color=txt_color, font="DejaVu-Sans-Bold", method='caption', size=(900, None))
            text_overlay = text_overlay.set_position('center').set_start(eff_start).set_end(eff_end)
            
            layers.append(screen)
            layers.append(text_overlay)

    # 6. Apply First 3-Second Hook Text
    if hook_text:
        hook_bg = ColorClip(size=(TARGET_W, TARGET_H), color=(0, 0, 0)).set_duration(3.0).set_start(0)
        hook_txt_clip = TextClip(hook_text, fontsize=140, color='white', font="DejaVu-Sans-Bold", method='caption', size=(900, None))
        hook_txt_clip = hook_txt_clip.set_position("center").set_duration(3.0).set_start(0)
        layers.append(hook_bg)
        layers.append(hook_txt_clip)

    # 7. Final Composite & Render
    final_video = CompositeVideoClip(layers, size=(TARGET_W, TARGET_H)).set_duration(sub_clip.duration)
    
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        preset="fast",
        logger=None
    )

    # Clean up memory
    sub_clip.close()
    video.close()
    final_video.close()
