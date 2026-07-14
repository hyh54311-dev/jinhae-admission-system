import os
import qrcode

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
qr_path = os.path.join(base_dir, 'scratch', 'jinhae_bot_qr.png')
os.makedirs(os.path.dirname(qr_path), exist_ok=True)

def main():
    print("Generating QR code for https://jinhae-bot2.vercel.app/ ...")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data('https://jinhae-bot2.vercel.app/')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)
    print(f"SUCCESS: QR code saved at {qr_path}")

if __name__ == '__main__':
    main()
