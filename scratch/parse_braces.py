import sys

def check_brackets(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    nesting = []
    line_num = 1
    col_num = 1
    
    in_string = False
    string_char = None
    in_comment = False
    comment_type = None  # 'single' or 'multi'
    
    i = 0
    while i < len(content):
        char = content[i]
        
        # Line number updates
        if char == '\n':
            line_num += 1
            col_num = 1
            if in_comment and comment_type == 'single':
                in_comment = False
        else:
            col_num += 1
            
        # String toggle
        if not in_comment:
            if in_string:
                if char == '\\':
                    i += 2  # skip next char
                    col_num += 1
                    continue
                if char == string_char:
                    in_string = False
            else:
                if char in ["'", '"', '`']:
                    in_string = True
                    string_char = char
                    
        # Comment toggle
        if not in_string:
            if in_comment:
                if comment_type == 'multi' and char == '*' and i + 1 < len(content) and content[i+1] == '/':
                    in_comment = False
                    i += 2
                    col_num += 1
                    continue
            else:
                if char == '/' and i + 1 < len(content):
                    if content[i+1] == '/':
                        in_comment = True
                        comment_type = 'single'
                        i += 2
                        col_num += 1
                        continue
                    elif content[i+1] == '*':
                        in_comment = True
                        comment_type = 'multi'
                        i += 2
                        col_num += 1
                        continue
                        
        # Bracket count
        if not in_string and not in_comment:
            if char == '{':
                nesting.append((line_num, col_num - 1))
            elif char == '}':
                if not nesting:
                    print(f"ERROR: Extra closing brace '}}' at line {line_num}, column {col_num - 1}")
                else:
                    nesting.pop()
                    
        i += 1
        
    if nesting:
        print(f"ERROR: {len(nesting)} unclosed opening brace(s) remaining:")
        for line, col in nesting:
            print(f" -> Opening brace '{{' at line {line}, col {col}")
    else:
        print("Braces check: All matched perfectly!")

if __name__ == '__main__':
    check_brackets("문학_탐구보고서_웹앱_Code.gs")
