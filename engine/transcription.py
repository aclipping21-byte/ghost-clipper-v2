import os
import sys
from deepgram import DeepgramClient, PrerecordedOptions

def get_transcript(audio_path):
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        print("Error: DEEPGRAM_API_KEY is missing.")
        sys.exit(1)

    try:
        client = DeepgramClient(api_key)
        
        with open(audio_path, "rb") as file:
            buffer_data = file.read()

        payload = {"buffer": buffer_data}
        options = PrerecordedOptions(
            model="nova-3",
            smart_format=True,
            utterances=True, # Forces sentence-level breakdown
            punctuate=True
        )

        response = client.listen.prerecorded.v("1").transcribe_file(payload, options)
        
        # Format transcript with timestamps for the AI Director
        formatted_transcript = ""
        utterances = response.results.utterances
        if utterances:
            for utterance in utterances:
                start_s = round(utterance.start, 1)
                formatted_transcript += f"[{start_s}s] {utterance.transcript}\n"
        else:
            # Fallback if utterances fail
            formatted_transcript = response.results.channels[0].alternatives[0].transcript

        return formatted_transcript

    except Exception as e:
        print(f"Deepgram transcription failed: {e}")
        sys.exit(1)
