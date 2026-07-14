import os

def main():
    output_lines = []
    
    for filename in os.listdir('.'):
        if filename.endswith('.md'):
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                
                # Check if first line contains 문학 or 화법 or 작문
                if "문학" in first_line or "화법" in first_line or "작문" in first_line:
                    # Read entire content
                    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    output_lines.append("=======================================")
                    output_lines.append(f"Filename: {filename}")
                    output_lines.append("---------------------------------------")
                    output_lines.append(content)
                    output_lines.append("\n")
            except Exception as e:
                output_lines.append(f"Error checking {filename}: {e}\n")
                
    with open("scratch/exam_findings.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Saved findings to scratch/exam_findings.txt")

if __name__ == '__main__':
    main()
