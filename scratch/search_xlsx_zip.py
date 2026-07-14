import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"

try:
    with zipfile.ZipFile(file_path, 'r') as z:
        print("Searching for 'forms' or 'http' inside xlsx ZIP:")
        for name in z.namelist():
            try:
                content = z.read(name)
                # Check for forms in bytes
                if b'forms' in content or b'google.com/forms' in content:
                    print(f"  Found match in ZIP file: {name}")
                    # Print context
                    idx = content.find(b'forms')
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 200)
                    print("  Snippet:", content[start:end])
            except Exception as e:
                pass
except Exception as e:
    print("Error:", e)
print("Done.")
