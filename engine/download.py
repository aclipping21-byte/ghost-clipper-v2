import requests
import re
from urllib.parse import urlparse

def resolve_buzzheavier_url(url):
    """
    Checks if the URL is a Buzzheavier link. If so, it scrapes the page for 
    the hidden HTMX download endpoint and extracts the direct video file URL.
    """
    if "buzzheavier.com" not in url.lower():
        return url
        
    print("Detected Buzzheavier link! Extracting direct video URL...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    # 1. Fetch the main Buzzheavier page
    page_resp = requests.get(url, headers=headers)
    page_resp.raise_for_status()
    
    # 2. Find the download endpoint using regex
    match = re.search(r'hx-get="([^"]+/download)"', page_resp.text)
    if not match:
        raise Exception("Could not find the download button on the Buzzheavier page.")
        
    download_endpoint = match.group(1)
    
    # 3. Construct the hidden API URL
    parsed = urlparse(url)
    api_url = f"{parsed.scheme}://{parsed.netloc}{download_endpoint}"
    
    # 4. Request the direct link using Buzzheavier's required HTMX headers
    hx_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'HX-Request': 'true',
        'HX-Current-URL': url
    }
    api_resp = requests.get(api_url, headers=hx_headers, allow_redirects=False)
    
    # The direct link is returned in the HX-Redirect header
    direct_url = api_resp.headers.get("HX-Redirect") or api_resp.headers.get("Location")
    
    if not direct_url:
        raise Exception("Failed to extract direct download link from Buzzheavier API.")
        
    # Handle relative redirects just in case
    if direct_url.startswith("/"):
        direct_url = f"{parsed.scheme}://{parsed.netloc}{direct_url}"
        
    return direct_url

def download_video(url, output_path):
    """
    Downloads a raw video file from a public URL in chunks 
    to handle large files without running out of memory.
    Now supports Buzzheavier links natively!
    """
    # Automatically resolve Buzzheavier URLs to direct links
    resolved_url = resolve_buzzheavier_url(url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    response = requests.get(resolved_url, stream=True, headers=headers)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
