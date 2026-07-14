import win32com.client
try:
    print("win32com.client imported successfully.")
    import pyhwpx
    print("pyhwpx imported successfully.")
    hwp = pyhwpx.Hwp(visible=True)
    print("HWP initialized successfully!")
    hwp.Quit()
    print("HWP quit successfully!")
except Exception as e:
    print(f"Error occurred: {e}")
