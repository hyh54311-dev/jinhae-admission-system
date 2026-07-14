import os

def main():
    print("=== Listing markdown files and their headers ===")
    for f in os.listdir('.'):
        if f.endswith('.md'):
            print(f"- File: {f}")
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    first_lines = [file.readline().strip() for _ in range(5)]
                    for idx, line in enumerate(first_lines):
                        if line:
                            print(f"    Line {idx+1}: {line}")
            except Exception as e:
                print(f"    Error reading: {e}")

if __name__ == '__main__':
    main()
