import os
import urllib.request
import urllib.parse

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'

qr_targets = {
    'qr_template_repo.png': 'https://github.com/hyh54311-dev/jinhae-k-momentum-bot',
    'qr_kis_portal.png': 'https://apiportal.koreainvestment.com',
    'qr_kis_main.png': 'https://apiportal.koreainvestment.com',
    'qr_kis_guide.png': 'https://apiportal.koreainvestment.com/intro',
    'qr_kis_github.png': 'https://github.com/koreainvestment/open-trading-api'
}

for filename, url in qr_targets.items():
    encoded_url = urllib.parse.quote(url)
    api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_url}&margin=10"
    
    file_dest = os.path.join(output_dir, filename)
    artifact_dest = os.path.join(artifact_dir, filename)
    
    print(f"Downloading QR for {url} -> {filename}")
    urllib.request.urlretrieve(api_url, file_dest)
    urllib.request.urlretrieve(api_url, artifact_dest)

print("ALL 5 HIGH-RES QR CODE IMAGES GENERATED SUCCESSFULLY!")
