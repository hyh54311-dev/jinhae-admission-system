import os

def search_files():
    keywords = ["1차고사", "문항", "출제", "문학", "화법과 작문", "화법", "화작", "고사", "문항수", "배점"]
    print("Searching for exam-related files...")
    
    # We will look inside the local files in the current folder (excluding binary or non-txt files)
    supported_extensions = ['.txt', '.md', '.py', '.js', '.csv', '.json']
    
    for filename in os.listdir('.'):
        if os.path.isdir(filename):
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_extensions:
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_idx, line in enumerate(f, 1):
                        matched_kws = [kw for kw in keywords if kw in line]
                        if matched_kws:
                            # Let's print matching lines
                            # Keep it clean: print filename and matching line
                            clean_line = line.strip()
                            if len(clean_line) > 150:
                                clean_line = clean_line[:150] + "..."
                            print(f"[{filename}:{line_idx}] ({', '.join(matched_kws)}): {clean_line}")
            except Exception as e:
                pass

if __name__ == '__main__':
    search_files()
