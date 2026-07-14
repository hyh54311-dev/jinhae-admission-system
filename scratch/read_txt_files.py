import sys

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_file(name):
    print(f"=== {name} ===")
    try:
        with open(name, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading: {e}")
    print("-" * 40)

def main():
    print_file("alert_log.txt")
    print_file("last_error.txt")

if __name__ == "__main__":
    main()
