"""Generate TabBar and in-app icon PNGs (Luckin-style line icons)."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent / 'src' / 'static'
TAB_DIR = ROOT / 'tabbar'
ICON_DIR = ROOT / 'icons'
SIZE_TAB = 81
SIZE_ICON = 96

GRAY = (153, 153, 153, 255)
NAVY = (91, 168, 207, 255)
WHITE = (255, 255, 255, 255)


def new_canvas(size, bg=(0, 0, 0, 0)):
    return Image.new('RGBA', (size, size), bg)


def stroke(draw, points, color, width=4):
    draw.line(points, fill=color, width=width, joint='curve')


def save_pair(name, drawer):
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for color, suffix in ((GRAY, ''), (NAVY, '-active')):
        img = new_canvas(SIZE_TAB)
        d = ImageDraw.Draw(img)
        drawer(d, SIZE_TAB, color)
        img.save(TAB_DIR / f'{name}{suffix}.png')
    img = new_canvas(SIZE_ICON)
    d = ImageDraw.Draw(img)
    drawer(d, SIZE_ICON, NAVY)
    img.save(ICON_DIR / f'{name}.png')


def draw_home(d, s, c):
    m = s * 0.18
    stroke(d, [(m, s * 0.45), (s * 0.5, m), (s - m, s * 0.45)], c)
    stroke(d, [(s * 0.28, s * 0.45), (s * 0.28, s * 0.78), (s * 0.72, s * 0.78), (s * 0.72, s * 0.45)], c)


def draw_checkin(d, s, c):
    m = s * 0.2
    stroke(d, [(m, s * 0.28), (s - m, s * 0.28), (s - m, s * 0.78), (m, s * 0.78), (m, s * 0.28)], c)
    stroke(d, [(m, s * 0.4), (s - m, s * 0.4)], c)
    stroke(d, [(s * 0.34, s * 0.58), (s * 0.46, s * 0.7), (s * 0.68, s * 0.48)], c, 5)


def draw_training(d, s, c):
    """Open book — 训练题库"""
    m = s * 0.22
    stroke(d, [(m, s * 0.24), (m, s * 0.76), (s * 0.5, s * 0.76), (s * 0.5, s * 0.24), (m, s * 0.24)], c)
    stroke(d, [(s * 0.5, s * 0.24), (s * 0.5, s * 0.76), (s - m, s * 0.76), (s - m, s * 0.24), (s * 0.5, s * 0.24)], c)
    stroke(d, [(s * 0.5, s * 0.24), (s * 0.5, s * 0.76)], c)


def draw_ai(d, s, c):
    cx, cy = s * 0.5, s * 0.5
    for i in range(4):
        ang = i * 90 + 45
        import math
        rad = math.radians(ang)
        x1 = cx + math.cos(rad) * s * 0.12
        y1 = cy + math.sin(rad) * s * 0.12
        x2 = cx + math.cos(rad) * s * 0.28
        y2 = cy + math.sin(rad) * s * 0.28
        stroke(d, [(x1, y1), (x2, y2)], c, 4)
    d.ellipse([cx - s * 0.1, cy - s * 0.1, cx + s * 0.1, cy + s * 0.1], outline=c, width=4)


def draw_profile(d, s, c):
    cx = s * 0.5
    d.ellipse([cx - s * 0.12, s * 0.22, cx + s * 0.12, s * 0.46], outline=c, width=4)
    stroke(d, [(cx - s * 0.22, s * 0.78), (cx - s * 0.22, s * 0.58), (cx + s * 0.22, s * 0.58), (cx + s * 0.22, s * 0.78)], c)


def draw_mic(d, s, c):
    cx = s * 0.5
    d.rounded_rectangle([cx - s * 0.1, s * 0.2, cx + s * 0.1, s * 0.52], radius=8, outline=c, width=4)
    stroke(d, [(cx, s * 0.52), (cx, s * 0.68)], c)
    stroke(d, [(cx - s * 0.16, s * 0.68), (cx + s * 0.16, s * 0.68)], c)


def draw_target(d, s, c):
    cx, cy = s * 0.5, s * 0.5
    for r in (0.28, 0.18, 0.08):
        d.ellipse([cx - s * r, cy - s * r, cx + s * r, cy + s * r], outline=c, width=4)


def draw_bolt(d, s, c):
    stroke(d, [(s * 0.55, s * 0.18), (s * 0.32, s * 0.52), (s * 0.5, s * 0.52), (s * 0.38, s * 0.82), (s * 0.68, s * 0.44), (s * 0.5, s * 0.44), (s * 0.55, s * 0.18)], c, 4)


def draw_video(d, s, c):
    stroke(d, [(s * 0.2, s * 0.28), (s * 0.2, s * 0.72), (s * 0.58, s * 0.72), (s * 0.58, s * 0.28), (s * 0.2, s * 0.28)], c)
    stroke(d, [(s * 0.58, s * 0.42), (s * 0.8, s * 0.32), (s * 0.8, s * 0.68), (s * 0.58, s * 0.58)], c)


def draw_robot(d, s, c):
    stroke(d, [(s * 0.28, s * 0.36), (s * 0.72, s * 0.36), (s * 0.72, s * 0.72), (s * 0.28, s * 0.72), (s * 0.28, s * 0.36)], c)
    stroke(d, [(s * 0.5, s * 0.2), (s * 0.5, s * 0.36)], c)
    d.ellipse([s * 0.36, s * 0.48, s * 0.42, s * 0.54], fill=c)
    d.ellipse([s * 0.58, s * 0.48, s * 0.64, s * 0.54], fill=c)


def draw_calendar(d, s, c):
    draw_checkin(d, s, c)


def draw_trophy(d, s, c):
    stroke(d, [(s * 0.35, s * 0.24), (s * 0.65, s * 0.24), (s * 0.6, s * 0.52), (s * 0.4, s * 0.52), (s * 0.35, s * 0.24)], c)
    stroke(d, [(s * 0.5, s * 0.52), (s * 0.5, s * 0.64)], c)
    stroke(d, [(s * 0.36, s * 0.64), (s * 0.64, s * 0.64), (s * 0.64, s * 0.72), (s * 0.36, s * 0.72), (s * 0.36, s * 0.64)], c)


def draw_book(d, s, c):
    stroke(d, [(s * 0.3, s * 0.22), (s * 0.3, s * 0.78), (s * 0.7, s * 0.78), (s * 0.7, s * 0.22), (s * 0.3, s * 0.22)], c)
    stroke(d, [(s * 0.5, s * 0.22), (s * 0.5, s * 0.78)], c)


def draw_search(d, s, c):
    cx, cy = s * 0.44, s * 0.44
    d.ellipse([cx - s * 0.18, cy - s * 0.18, cx + s * 0.18, cy + s * 0.18], outline=c, width=4)
    stroke(d, [(cx + s * 0.12, cy + s * 0.12), (s * 0.74, s * 0.74)], c)


def draw_fire(d, s, c):
    stroke(d, [(s * 0.5, s * 0.18), (s * 0.68, s * 0.42), (s * 0.62, s * 0.58), (s * 0.72, s * 0.72), (s * 0.5, s * 0.82), (s * 0.28, s * 0.72), (s * 0.38, s * 0.58), (s * 0.32, s * 0.42), (s * 0.5, s * 0.18)], c, 4)


def draw_star(d, s, c):
    import math
    cx, cy = s * 0.5, s * 0.5
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = s * 0.28 if i % 2 == 0 else s * 0.12
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    stroke(d, pts + [pts[0]], c, 4)


def draw_gift(d, s, c):
    stroke(d, [(s * 0.22, s * 0.42), (s * 0.78, s * 0.42), (s * 0.78, s * 0.78), (s * 0.22, s * 0.78), (s * 0.22, s * 0.42)], c)
    stroke(d, [(s * 0.22, s * 0.52), (s * 0.78, s * 0.52)], c)
    stroke(d, [(s * 0.5, s * 0.42), (s * 0.5, s * 0.78)], c)
    stroke(d, [(s * 0.5, s * 0.22), (s * 0.38, s * 0.32), (s * 0.5, s * 0.42), (s * 0.62, s * 0.32), (s * 0.5, s * 0.22)], c)


def draw_list(d, s, c):
    for y in (0.3, 0.5, 0.7):
        stroke(d, [(s * 0.22, s * y), (s * 0.78, s * y)], c)
        d.ellipse([s * 0.16, s * y - 4, s * 0.24, s * y + 4], fill=c)


def draw_bell(d, s, c):
    stroke(d, [(s * 0.35, s * 0.32), (s * 0.35, s * 0.52), (s * 0.65, s * 0.52), (s * 0.65, s * 0.32)], c)
    stroke(d, [(s * 0.28, s * 0.52), (s * 0.72, s * 0.52), (s * 0.68, s * 0.68), (s * 0.32, s * 0.68), (s * 0.28, s * 0.52)], c)
    d.ellipse([s * 0.46, s * 0.68, s * 0.54, s * 0.76], fill=c)


def draw_moon(d, s, c):
    d.arc([s * 0.24, s * 0.24, s * 0.76, s * 0.76], start=60, end=300, fill=None, width=4)


def draw_info(d, s, c):
    cx = s * 0.5
    d.ellipse([cx - s * 0.28, s * 0.22, cx + s * 0.28, s * 0.78], outline=c, width=4)
    d.ellipse([cx - 4, s * 0.34, cx + 4, s * 0.42], fill=c)
    stroke(d, [(cx, s * 0.5), (cx, s * 0.66)], c, 5)


def draw_briefcase(d, s, c):
    m = s * 0.22
    stroke(d, [(m, s * 0.38), (s - m, s * 0.38), (s - m, s * 0.78), (m, s * 0.78), (m, s * 0.38)], c)
    stroke(d, [(s * 0.36, s * 0.38), (s * 0.36, s * 0.28), (s * 0.64, s * 0.28), (s * 0.64, s * 0.38)], c)
    stroke(d, [(s * 0.42, s * 0.28), (s * 0.42, s * 0.22), (s * 0.58, s * 0.22), (s * 0.58, s * 0.28)], c)
    stroke(d, [(s * 0.5, s * 0.48), (s * 0.5, s * 0.62)], c)


def main():
    save_pair('home', draw_home)
    save_pair('checkin', draw_checkin)
    save_pair('training', draw_training)
    save_pair('ai', draw_ai)
    save_pair('profile', draw_profile)

    for name, drawer in [
        ('mic', draw_mic), ('target', draw_target), ('bolt', draw_bolt),
        ('video', draw_video), ('robot', draw_robot), ('calendar', draw_calendar),
        ('trophy', draw_trophy), ('book', draw_book), ('search', draw_search),
        ('fire', draw_fire), ('star', draw_star), ('gift', draw_gift), ('list', draw_list),
        ('moon', draw_moon), ('bell', draw_bell), ('info', draw_info),
        ('briefcase', draw_briefcase),
    ]:
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        img = new_canvas(SIZE_ICON)
        d = ImageDraw.Draw(img)
        drawer(d, SIZE_ICON, NAVY)
        img.save(ICON_DIR / f'{name}.png')

    print('Icons generated:', TAB_DIR, ICON_DIR)


if __name__ == '__main__':
    main()
