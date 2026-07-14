def search_file(path, keyword):
    print(f"=== Searching '{keyword}' in {path} ===")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                if keyword in line:
                    print(f"{idx}: {line.strip()}")
    except Exception as e:
        print(f"Error reading {path}: {e}")

def main():
    search_file("daily_news.py", "PAUSE_WEEKDAY")
    search_file("cloud_daily_news.py", "PAUSE_WEEKDAY")
    search_file("run_news_once.py", "PAUSE_WEEKDAY")
    search_file("weekday_news_gas.js", "PAUSE_WEEKDAY")

if __name__ == '__main__':
    main()
