import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/form.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("Page Title:", soup.title.string if soup.title else "No Title")

# Find all question labels. Usually Google Forms labels are in divs with class containing 'M7eC3' or role="heading" or similar.
# Let's search for anything with role="heading"
headings = soup.find_all(role="heading")
print(f"\nFound {len(headings)} headings:")
for h in headings:
    print("  ", h.text.strip())

# Find all buttons (like '다음', '제출')
buttons = soup.find_all(role="button")
print(f"\nFound {len(buttons)} buttons:")
for b in buttons:
    text = b.text.strip()
    if text:
        print("  Button:", text)
        
# Find input fields or selectors
inputs = soup.find_all(['input', 'select', 'textarea'])
print(f"\nFound {len(inputs)} input/select/textarea elements:")
for ip in inputs:
    print(f"  Tag: {ip.name}, type: {ip.get('type')}, name: {ip.get('name')}, id: {ip.get('id')}")
