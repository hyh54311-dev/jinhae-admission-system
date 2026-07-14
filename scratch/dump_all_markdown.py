import os

def main():
    output_lines = []
    
    for filename in os.listdir('.'):
        if filename.endswith('.md'):
            output_lines.append("=======================================")
            output_lines.append(f"Original Filename: {filename}")
            output_lines.append("---------------------------------------")
            
            # Read and dump the file. We'll try reading with utf-8 first, then cp949
            content = None
            for encoding in ['utf-8', 'cp949']:
                try:
                    with open(filename, 'r', encoding=encoding) as f:
                        content = f.read()
                    output_lines.append(f"(Read successfully using {encoding})")
                    break
                except Exception:
                    continue
            
            if content is None:
                # Fallback to ignore errors
                try:
                    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    output_lines.append("(Read with UTF-8 ignore errors)")
                except Exception as e:
                    content = f"Failed to read file: {e}"
            
            output_lines.append(content)
            output_lines.append("\n")
            
    with open("scratch/all_markdown_dump.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Dumped all markdown files to scratch/all_markdown_dump.txt")

if __name__ == '__main__':
    main()
