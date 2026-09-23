from PIL import Image, ImageDraw

def create_applitrack_icon():
    # 256x256 high-resolution canvas
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Rounded App Tile Background
    draw.rounded_rectangle([12, 12, 244, 244], radius=56, fill="#0f172a", outline="#38bdf8", width=8)

    # 2. Briefcase Handle
    draw.rounded_rectangle([92, 54, 164, 88], radius=14, fill=None, outline="#38bdf8", width=12)

    # 3. Briefcase Body
    draw.rounded_rectangle([44, 86, 212, 202], radius=24, fill="#1e293b", outline="#6366f1", width=10)

    # 4. Accent Center Buckle
    draw.rounded_rectangle([112, 124, 144, 158], radius=8, fill="#38bdf8")

    # Save as multi-size Windows icon file
    img.save("app_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("✔ 'app_icon.ico' created successfully!")

if __name__ == "__main__":
    create_applitrack_icon()