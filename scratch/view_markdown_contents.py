import os

def main():
    output_lines = []
    
    # List all files and check if they relate to literature or writing
    for filename in os.listdir('.'):
        if filename.endswith('.md'):
            try:
                # Read file
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check if it has literature (문학) or writing (화법, 작문) or questions (문항, 출제)
                keywords = ["문학", "화법", "작문", "출제", "문항"]
                if any(kw in content for kw in keywords) or any(kw in filename for kw in keywords):
                    output_lines.append("=======================================")
                    output_lines.append(f"Filename: {filename}")
                    output_lines.append("---------------------------------------")
                    output_lines.append(content)
                    output_lines.append("\n")
            except Exception as e:
                output_lines.append(f"Error reading {filename}: {e}\n")
                
    with open("scratch/markdown_details.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Saved details to scratch/markdown_details.txt")

if __name__ == '__main__':
    main()
