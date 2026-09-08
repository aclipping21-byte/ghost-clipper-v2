import os
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

def get_transcript(audio_path):
    print(f"Starting Deepgram transcription for {audio_path}...")
    
    # 1. Verify the API key is present
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is missing.")

    # 2. Initialize the client
    deepgram = DeepgramClient(api_key)

    # 3. Read the extracted audio file safely
    with open(audio_path, "rb") as file:
        buffer_data = file.read()

    payload: FileSource = {
        "buffer": buffer_data,
    }

    # 4. Request the newest Nova-3 model and ask for utterances (timestamped sentences)
    options = PrerecordedOptions(
        model="nova-3",
        smart_format=True,
        utterances=True,
        punctuate=True
    )

    # 5. Send to Deepgram
    response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
    
    # 6. Format the output specifically for Gemini
    data = response.to_dict()
    formatted_transcript = ""
    
    utterances = data.get("results", {}).get("utterances", [])
    
    if not utterances:
        print("Warning: No speech detected in audio.")
        return ""

    for u in utterances:
        start_time = round(u.get("start", 0.0), 2)
        end_time = round(u.get("end", 0.0), 2)
        text = u.get("transcript", "")
        # Creates a format like: [12.5 - 15.2] This is a great hook.
        formatted_transcript += f"[{start_time} - {end_time}] {text}\n"

    print("Transcription complete!")
    return formatted_transcript

if __name__ == "__main__":
    # This block allows us to test the file independently later if needed
    pass
