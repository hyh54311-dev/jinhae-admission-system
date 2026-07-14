import os
import base64
from PIL import Image

def main():
    logo_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\school_logo.png"
    out_txt_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\logo_base64.txt"
    
    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} not found.")
        return
        
    print(f"Opening {logo_path}...")
    img = Image.open(logo_path)
    
    # Resize keeping aspect ratio
    max_width = 300
    w_percent = (max_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    resized_img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
    
    # Save to memory buffer
    import io
    buffer = io.BytesIO()
    resized_img.save(buffer, format="PNG", optimize=True)
    img_bytes = buffer.getvalue()
    
    # Base64 encode
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    data_uri = f"data:image/png;base64,{base64_str}"
    
    # Ensure scratch dir exists
    os.makedirs(os.path.dirname(out_txt_path), exist_ok=True)
    
    # Write to file
    with open(out_txt_path, 'w', encoding='utf-8') as f:
        f.write(data_uri)
        
    print(f"Success! Base64 URI saved to {out_txt_path} ({len(data_uri)} characters, approx {len(data_uri)/1024:.2f} KB)")

if __name__ == "__main__":
    main()
