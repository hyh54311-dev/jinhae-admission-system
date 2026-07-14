import os
import sys
import io

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    
    root_dir = "."
    keywords = ["3학년", "기말", "2차고사", "2차 시험", "2차 지필"]
    exclude_files = ["scan_result.json", "all_files.txt", "target_files.txt", "dry_run_merge_phase2.txt", "pdf_extracted.txt", "clean_text.txt"]
    exclude_dirs = [".git", "__pycache__", ".agents", "temp_unzip", "temp"]

    print("Searching workspace...")
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            if filename in exclude_files:
                continue
            if filename.endswith((".txt", ".md", ".py", ".js", ".json", ".html")):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, encoding='utf-8', errors='ignore') as f:
                        for line_idx, line in enumerate(f, 1):
                            line_lower = line.lower()
                            if any(kw in line for kw in keywords):
                                matches.append((filepath, line_idx, line.strip()))
                except Exception as e:
                    pass

    print(f"Found {len(matches)} matches:")
    for filepath, line_idx, line in matches[:100]: # Print top 100
        print(f"{filepath}:{line_idx}: {line}")

if __name__ == '__main__':
    main()
