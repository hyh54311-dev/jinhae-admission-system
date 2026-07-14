import os

for root, dirs, files in os.walk('.'):
    for f in files:
        if 'standard' in f.lower():
            print(os.path.join(root, f))
