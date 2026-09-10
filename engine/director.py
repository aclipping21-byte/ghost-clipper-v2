import os
import json
from openai import OpenAI

def analyze_transcript_and_plan_edits(transcript):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is missing.")

    # Initialize the OpenAI client pointing to OpenRouter's servers
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

        # The Bulletproof Loop (Updated September 2026)
    fallback_models = [
        "openrouter/free",
        "thinkingmachines/inkling:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemma-4-31b-it:free"
    ]

    system_prompt = """You are an expert AI video director. Your job is to read a video transcript and find the most viral, engaging moments to turn into short-form clips (TikTok/Reels).
    You must reply strictly in valid JSON format matching this exact structure:
    {
        "clips": [
            {
                "start_time": 12.5,
                "end_time": 45.0,
                "title": "The most insane hook goes here"
            }
        ]
    }
    Only output JSON. Do not include markdown blocks. Do not include any other text."""

    user_prompt = f"Here is the transcript:\n\n{transcript}\n\nFind 1 to 3 viral clips and output the exact JSON."

    # The Bulletproof Loop
    for model in fallback_models:
        print(f"Director: Attempting to analyze transcript using {model}...")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Clean up the output just in case the AI added formatting blocks
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
                
            clips_data = json.loads(raw_content.strip())
            
            print(f"Success! Model {model} delivered the clips.")
            return clips_data["clips"]
            
        except Exception as e:
            print(f"Warning: Model {model} failed or returned invalid JSON.")
            print(f"Error details: {e}")
            print("Switching to next fallback model in 3, 2, 1...\n")
            continue
            
    # If the loop finishes without returning anything, all models failed
    raise RuntimeError("Critical Failure: All OpenRouter fallback models failed to generate clips.")
