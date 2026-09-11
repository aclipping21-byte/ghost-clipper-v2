import requests

def download_video(url, output_path):
    """
    Downloads a raw video file from a public URL in chunks 
    to handle large files without running out of memory.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
