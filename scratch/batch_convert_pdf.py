import win32com.client
import os
import glob
import sys

# Set encoding for stdout to avoid cp949 errors
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def batch_convert_hwp_to_pdf(folder_paths):
    try:
        print("Starting HWP application for PDF conversion...")
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckDLL")
        # Keep it invisible to not clutter the screen, but we know it works
        
        for folder in folder_paths:
            print(f"\nProcessing folder: {folder}")
            hwp_files = glob.glob(os.path.join(folder, "*.hwp"))
            
            for hwp_path in hwp_files:
                pdf_path = hwp_path.replace(".hwp", ".pdf")
                if os.path.exists(pdf_path):
                    print(f"Already exists, skipping: {os.path.basename(pdf_path)}")
                    continue
                    
                print(f"Converting: {os.path.basename(hwp_path)} -> PDF")
                try:
                    hwp.Open(hwp_path, "HWP", "forceopen:true")
                    
                    # Try FileSaveAsPdf first
                    try:
                        hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
                        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
                        hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                    except Exception:
                        # Fallback to SaveAs
                        hwp.SaveAs(pdf_path, "PDF", "")
                except Exception as e:
                    print(f"Failed to convert {os.path.basename(hwp_path)}: {e}")
                
        hwp.Quit()
        print("\nAll conversions finished!")
        
        # Notify the user
        ps_command = '[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); [System.Windows.Forms.MessageBox]::Show("모든 한글 파일의 PDF 변환이 완료되었습니다!", "변환 완료")'
        import subprocess
        subprocess.run(["powershell", "-Command", ps_command])
        
    except Exception as e:
        print(f"Critical error during conversion: {e}")

folders_to_convert = [
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록"
]

batch_convert_hwp_to_pdf(folders_to_convert)
