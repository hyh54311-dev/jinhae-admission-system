import subprocess

def main():
    p = subprocess.Popen(
        ["schtasks", "/query", "/tn", "Jeju_Air_JJIM_Reminder", "/xml"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    
    # Try decoding using cp949 since it's Windows Korean locale
    try:
        decoded_out = stdout.decode('cp949')
    except Exception:
        decoded_out = stdout.decode('utf-8', errors='ignore')
        
    print(decoded_out)

if __name__ == "__main__":
    main()
