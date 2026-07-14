import os
import sys
import webview

def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = get_executable_dir()
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    base_dir = get_resource_path('.')
    html_path = os.path.join(base_dir, 'PDF_Suite.html')
    
    # Create the webview window pointing to our HTML
    window = webview.create_window(
        title='Smart PDF Suite (진해고등학교)',
        url=html_path,
        width=1280,
        height=850,
        min_size=(1000, 700),
        resizable=True
    )
    
    # Start webview with the built-in HTTP server enabled
    webview.start(http_server=True)
