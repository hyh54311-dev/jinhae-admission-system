import os
import re
import json
import requests
import sys

def parse_form():
    form_id = '1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE'
    url = f'https://docs.google.com/forms/d/{form_id}/viewform'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return
            
        html = response.text
        
        # Find the start of var FB_PUBLIC_LOAD_DATA_
        marker = 'var FB_PUBLIC_LOAD_DATA_ ='
        idx = html.find(marker)
        if idx == -1:
            marker = 'var FB_PUBLIC_LOAD_DATA_='
            idx = html.find(marker)
            
        if idx == -1:
            print("Error: Could not find FB_PUBLIC_LOAD_DATA_ in the HTML.")
            return
            
        # Find the opening bracket of the array
        start_idx = html.find('[', idx + len(marker))
        if start_idx == -1:
            print("Error: Opening bracket not found.")
            return
            
        bracket_count = 0
        in_string = False
        escape = False
        quote_char = None
        data_str = None
        
        for i in range(start_idx, len(html)):
            char = html[i]
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if in_string:
                if char == quote_char:
                    in_string = False
                continue
            if char in ('"', "'"):
                in_string = True
                quote_char = char
                continue
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    data_str = html[start_idx:i+1]
                    break
                    
        if not data_str:
            print("Error: Bracket mismatch.")
            return
            
        data = json.loads(data_str)
        items = data[1][1]
        
        out_lines = []
        out_lines.append(f"Form Title: {data[1][8]}\n")
        
        for item in items:
            if not item: continue
            item_id = item[0]
            title = item[1]
            item_type = item[3]
            out_lines.append(f"- Item Title: {title}")
            out_lines.append(f"  Item Type: {item_type} (ID: {item_id})")
            
            try:
                sub_items = item[4]
                for sub in sub_items:
                    entry_id = sub[0]
                    out_lines.append(f"  Entry ID: entry.{entry_id}")
                    if len(sub) > 1 and sub[1]:
                        choices = [choice[0] for choice in sub[1]]
                        out_lines.append(f"  Choices: {choices}")
            except Exception as e:
                pass
            out_lines.append("-" * 50)
            
        output_txt = '\n'.join(out_lines)
        with open('scratch/form_structure.txt', 'w', encoding='utf-8') as f:
            f.write(output_txt)
        print("Success! Structure written to scratch/form_structure.txt")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    parse_form()
