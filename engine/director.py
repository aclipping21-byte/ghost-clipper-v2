import os
import json
from google import genai
from google.genai import types

SYSTEM_PROMPT = """
You are an elite short-form video editor and director for TikTok, Instagram Reels, and YouTube Shorts.
Your task is to analyze a transcript containing timestamps and identify up to 5 genuinely strong, high-retention clips.

CRITICAL RULES:
1. Prioritize strong hooks, viral potential, storytelling, and self-contained moments.
2. DO NOT select random or mediocre moments just to fill 5 clips. If only 2 or 3 moments are great, return only 2 or 3.
3. Every clip MUST work independently without requiring extra context.
4. Timestamps must strictly match the start and end of the spoken words in the transcript.
5. For each clip, decide on creative edits (e.g., hook text in the first 3 seconds, color flashes for emphasis, or text cards).

OUTPUT FORMAT:
You MUST respond with a valid JSON object matching this structure EXACTLY:
{
  "clips": [
    {
      "clip_id": 1,
      "title": "Short descriptive title",
      "score": 90,
      "start_time": 12.5,
      "end_time": 45.2,
      "rationale": "Why this clip works...",
      "formatting": {
        "aspect_ratio": "9:16"
      },
      "edits": [
        {
          "type": "hook_text",
          "text": "ATTENTION-GRABBING HOOK",
          "start": 0,
          "end": 3
        },
        {
          "type": "flash",
          "color": "white",
          "time": 3.5
        }
      ]
    }
  ]
}
"""

def analyze_transcript_and_plan_edits(timestamped_transcript):
    print("Sending transcript to Gemini Director...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    user_prompt = f"Analyze this transcript and output your editing plan in the requested JSON format:\n\n{timestamped_transcript}"

    # We use Gemini 2.5 Flash for high speed and structured JSON capabilities
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    try:
        director_plan = json.loads(response.text)
        print(f"Director successfully identified {len(director_plan.get('clips', []))} clip(s).")
        return director_plan
    except json.JSONDecodeError as e:
        print("Error: Gemini returned invalid JSON:", response.text)
        raise e

if __name__ == "__main__":
    pass
