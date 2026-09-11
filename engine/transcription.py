import os
import sys
from deepgram import DeepgramClient, PrerecordedOptions

def get_transcript(audio_path):
    # Used in Phase 1 for the AI Director
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
            utterances=True,
            punctuate=True
        )

        response = client.listen.prerecorded.v("1").transcribe_file(payload, options)
        
        formatted_transcript = ""
        utterances = response.results.utterances
        if utterances:
            for utterance in utterances:
                start_s = round(utterance.start, 1)
                formatted_transcript += f"[{start_s}s] {utterance.transcript}\n"
        else:
            formatted_transcript = response.results.channels[0].alternatives[0].transcript

        return formatted_transcript

    except Exception as e:
        print(f"Deepgram transcription failed: {e}")
        sys.exit(1)

def get_word_timestamps(audio_path):
    # Used in Phase 2 for exact frame-by-frame caption sync
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    client = DeepgramClient(api_key)
    with open(audio_path, "rb") as file:
        buffer_data = file.read()
        
    payload = {"buffer": buffer_data}
    options = PrerecordedOptions(model="nova-3", smart_format=True)
    
    response = client.listen.prerecorded.v("1").transcribe_file(payload, options)
    words = response.results.channels[0].alternatives[0].words
    
    # Return a clean list of dictionaries for the renderer
    return [{"word": w.word, "start": w.start, "end": w.end} for w in words]
