from pyhwpx import Hwp
import os

def inspect_hwp():
    hwp = Hwp()
    hwp.set_visible(False)
    
    template_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\수업 교환, 대강 계획서\2026학년도 수업 교환 및 대강 계획서(양식).hwp"
    
    if not os.path.exists(template_path):
        print(f"File not found: {template_path}")
        hwp.quit()
        return

    hwp.open(template_path)
    
    table_count = hwp.get_table_count()
    print(f"Total tables: {table_count}")
    
    for i in range(table_count):
        print(f"\nTable {i} contents:")
        # Try to read the first row of each table
        hwp.TableSelectTable(i)
        # Actually, let's just get the text from the table
        # We can use hwp.get_text() after moving to the table
        pass
    
    # Better approach: just find "대강" and see if it's in a table
    if hwp.find_all("대강"):
        print("Found '대강'")
        # Check if we are in a table
        if hwp.is_in_table():
            print("Currently in a table")
            # Move to the first cell of the current table
            # And print the row/column structure
    
    hwp.quit()

if __name__ == "__main__":
    inspect_hwp()
