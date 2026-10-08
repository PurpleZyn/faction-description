import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
CONFIG_PATH = ROOT / "faction_config.json"

TEXT = (246, 237, 250, 255)
TEXT_DIM = (207, 188, 218, 255)
PURPLE = (196, 79, 249, 255)
PURPLE_SOFT = (169, 78, 219, 255)
BLACK = (5, 3, 8, 255)
GREEN = (129, 238, 78, 255)


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def load_image(path):
    p = resolve(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing faction asset: {p.relative_to(ROOT)}")
    return Image.open(p).convert("RGBA")


def font(size, bold=True, condensed=False):
    candidates = []
    if condensed:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        ])
    if bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ])
    candidates.extend([
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ])
    for candidate in candidates:
        p = Path(candidate)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def fit_width(img, width):
    img = img.convert("RGBA")
    if img.width == width:
        return img
    h = max(1, round(img.height * width / img.width))
    return img.resize((width, h), Image.Resampling.LANCZOS)


def cover(img, width, height, focus_y=0.5):
    img = img.convert("RGBA")
    scale = max(width / img.width, height / img.height)
    nw, nh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - width) // 2)
    max_top = max(0, nh - height)
    top = int(max_top * max(0, min(1, focus_y)))
    return img.crop((left, top, left + width, top + height))


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap_text(draw, text, fnt, max_width):
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def vertical_gradient(width, height, top=(7, 3, 11), bottom=(19, 4, 30)):
    strip = Image.new("RGBA", (1, height), BLACK)
    px = strip.load()
    for y in range(height):
        t = y / max(1, height - 1)
        px[0, y] = tuple(round(top[i]*(1-t)+bottom[i]*t) for i in range(3)) + (255,)
    return strip.resize((width, height), Image.Resampling.NEAREST)


def add_brand_texture(img, seed=0):
    width, height = img.size
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-220, -160, 520, 580), fill=(96, 20, 137, 78))
    gd.ellipse((width - 520, height - 610, width + 180, height + 90), fill=(127, 28, 173, 74))
    gd.ellipse((width // 2 - 230, height // 2 - 260, width // 2 + 230, height // 2 + 260), fill=(72, 8, 110, 35))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)

    sparks = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sparks)
    for i in range(max(45, height // 15)):
        x = (i * 173 + 71 + seed * 31) % max(1, width - 40) + 20
        y = (i * 97 + 29 + seed * 47) % max(1, height - 40) + 20
        r = 1 + int(i % 3 == 0)
        a = 22 + (i * 11) % 42
        sd.ellipse((x-r, y-r, x+r, y+r), fill=(218, 121, 255, a))
    img = Image.alpha_composite(img, sparks.filter(ImageFilter.GaussianBlur(0.6)))

    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, width-9, height-9), radius=20, outline=(189, 83, 237, 210), width=3)
    d.rounded_rectangle((15, 15, width-16, height-16), radius=17, outline=(73, 31, 98, 180), width=1)
    return img


def draw_glow_text(canvas, xy, text, fnt, fill=TEXT, glow_color=(205, 91, 255, 210), stroke=0):
    x, y = xy
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((x, y), text, font=fnt, fill=glow_color, stroke_width=stroke, stroke_fill=glow_color)
    layer = layer.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(layer)
    d = ImageDraw.Draw(canvas)
    d.text((x+2, y+2), text, font=fnt, fill=(38, 10, 52, 255))
    d.text((x, y), text, font=fnt, fill=fill)


def draw_centered(canvas, text, y, fnt, fill=TEXT, glow=False):
    d = ImageDraw.Draw(canvas)
    w = text_width(d, text, fnt)
    x = (canvas.width - w) // 2
    if glow:
        draw_glow_text(canvas, (x, y), text, fnt, fill=fill)
    else:
        d.text((x, y), text, font=fnt, fill=fill)


def render_recruiting(cfg, hero, width):
    height = 205
    bg = cover(hero, width, height, focus_y=0.45)
    bg = ImageEnhance.Brightness(bg).enhance(0.38)
    bg = ImageEnhance.Contrast(bg).enhance(1.15)
    wash = Image.new("RGBA", bg.size, (37, 0, 49, 105))
    bg = Image.alpha_composite(bg, wash)

    d = ImageDraw.Draw(bg)
    brand = font(37, bold=True, condensed=True)
    headline = font(54, bold=True, condensed=True)
    detail = font(24, bold=True, condensed=True)
    req = font(22, bold=True, condensed=True)
    cta = font(21, bold=True, condensed=True)

    d.text((38, 24), cfg["brand"], font=brand, fill=(244, 217, 255, 255))
    d.text((38, 67), cfg["headline"], font=headline, fill=GREEN, stroke_width=2, stroke_fill=(28, 64, 15, 255))
    d.text((42, 129), cfg["details"], font=detail, fill=TEXT)
    d.text((42, 161), cfg["requirements"], font=req, fill=(229, 218, 234, 255))

    cta_w = text_width(d, cfg["cta"], cta)
    d.text((width-cta_w-40, 162), cfg["cta"], font=cta, fill=(246, 112, 255, 255))
    d.line((width-cta_w-42, 189, width-36, 189), fill=(210, 72, 240, 180), width=2)
    return bg


def render_hero(hero, width):
    hero = fit_width(hero, width)
    d = ImageDraw.Draw(hero)
    d.rectangle((0, 0, hero.width-1, hero.height-1), outline=(91, 37, 119, 200), width=2)
    return hero


def card_metrics(draw, items, card_width, body_font):
    text_max = card_width - 92
    total = 92
    for item in items:
        lines = wrap_text(draw, item, body_font, text_max)
        total += len(lines) * 31 + 14
    return total + 16


def draw_card(canvas, xy, title, items):
    x, y, w, h = xy
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x+8, y+10, x+w+8, y+h+10), radius=22, fill=(0, 0, 0, 150))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((x, y, x+w, y+h), radius=22, fill=(7, 5, 12, 230), outline=(178, 75, 225, 235), width=3)
    d.rounded_rectangle((x+7, y+7, x+w-7, y+h-7), radius=18, outline=(72, 31, 98, 210), width=1)

    title_font = font(28, bold=True, condensed=True)
    body_font = font(22, bold=True)
    t = title.upper()
    tw = text_width(d, t, title_font)
    d.text((x+(w-tw)//2, y+24), t, font=title_font, fill=(230, 190, 249, 255))
    d.line((x+30, y+68, x+w-30, y+68), fill=(120, 45, 160, 165), width=2)

    cursor = y + 92
    max_text = w - 92
    for item in items:
        lines = wrap_text(d, item, body_font, max_text)
        bullet_y = cursor + 9
        d.ellipse((x+28, bullet_y, x+40, bullet_y+12), fill=PURPLE)
        line_y = cursor
        for line in lines:
            d.text((x+56, line_y), line, font=body_font, fill=TEXT)
            line_y += 31
        cursor = line_y + 14


def draw_title(canvas, title, y, size=60):
    fnt = font(size, bold=True, condensed=True)
    d = ImageDraw.Draw(canvas)
    tw = text_width(d, title, fnt)
    draw_glow_text(canvas, ((canvas.width-tw)//2, y), title, fnt, fill=TEXT)
    box = d.textbbox((0, 0), title, font=fnt)
    return y + (box[3]-box[1]) + 18


def render_about(cfg, width):
    probe = Image.new("RGBA", (width, 100), BLACK)
    pd = ImageDraw.Draw(probe)
    body = font(22, bold=True)
    side, gap = 54, 26
    card_w = (width - side*2 - gap)//2
    left_h = card_metrics(pd, cfg["left_items"], card_w, body)
    right_h = card_metrics(pd, cfg["right_items"], card_w, body)
    card_h = max(left_h, right_h, 430)

    title_top = 42
    title_space = 96
    card_y = title_top + title_space
    safe_h = 128
    safe_gap = 28
    bottom = 34
    height = card_y + card_h + safe_gap + safe_h + bottom

    canvas = add_brand_texture(vertical_gradient(width, height), seed=1)
    draw_title(canvas, cfg["title"], title_top, 60)
    draw_card(canvas, (side, card_y, card_w, card_h), cfg["left_title"], cfg["left_items"])
    draw_card(canvas, (side+card_w+gap, card_y, card_w, card_h), cfg["right_title"], cfg["right_items"])

    box_y = card_y + card_h + safe_gap
    box_x, box_w = 86, width - 172
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((box_x, box_y, box_x+box_w, box_y+safe_h), radius=18, fill=(9, 5, 15, 230), outline=(163, 61, 211, 235), width=3)
    f1, f2, f3 = font(27, True, True), font(35, True, True), font(20, True)
    for text, fnt, yy, fill in [
        (cfg["safe_space_title"], f1, box_y+18, (218, 174, 241, 255)),
        (cfg["safe_space_body"], f2, box_y+51, TEXT),
        (cfg["safe_space_note"], f3, box_y+94, (176, 114, 209, 255)),
    ]:
        tw = text_width(d, text, fnt)
        d.text(((width-tw)//2, yy), text, font=fnt, fill=fill)
    return canvas


def render_rogue_code(cfg, width):
    probe = Image.new("RGBA", (width, 100), BLACK)
    pd = ImageDraw.Draw(probe)
    body = font(22, bold=True)
    side, gap = 54, 26
    card_w = (width - side*2 - gap)//2
    left_h = card_metrics(pd, cfg["left_items"], card_w, body)
    right_h = card_metrics(pd, cfg["right_items"], card_w, body)
    card_h = max(left_h, right_h, 430)

    title_top = 42
    title_space = 100
    intro_y = title_top + title_space
    intro_h = 142
    card_y = intro_y + intro_h + 30
    height = card_y + card_h + 34

    canvas = add_brand_texture(vertical_gradient(width, height, top=(6, 3, 10), bottom=(20, 4, 30)), seed=2)
    draw_title(canvas, cfg["title"], title_top, 66)
    d = ImageDraw.Draw(canvas)

    intro_x, intro_w = 74, width - 148
    d.rounded_rectangle((intro_x, intro_y, intro_x+intro_w, intro_y+intro_h), radius=18, fill=(8, 5, 13, 230), outline=(168, 68, 219, 235), width=3)
    intro_font, emphasis_font = font(24, True, True), font(29, True, True)
    lines = wrap_text(d, cfg["intro"], intro_font, intro_w-70)
    yy = intro_y + 23
    for line in lines:
        tw = text_width(d, line, intro_font)
        d.text(((width-tw)//2, yy), line, font=intro_font, fill=TEXT_DIM)
        yy += 31
    tw = text_width(d, cfg["emphasis"], emphasis_font)
    d.text(((width-tw)//2, intro_y+96), cfg["emphasis"], font=emphasis_font, fill=(220, 135, 255, 255))

    draw_card(canvas, (side, card_y, card_w, card_h), cfg["left_title"], cfg["left_items"])
    draw_card(canvas, (side+card_w+gap, card_y, card_w, card_h), cfg["right_title"], cfg["right_items"])
    return canvas


def render_footer_gif(cfg, hero, out_path, width):
    height = 320
    bg_base = cover(hero, width, height, focus_y=0.5)
    bg_base = ImageEnhance.Brightness(bg_base).enhance(0.18)
    bg_base = ImageEnhance.Color(bg_base).enhance(0.45)
    frames = max(2, int(cfg.get("frames", 8)))
    duration = int(cfg.get("frame_duration_ms", 100))

    out = []
    title_font = font(76, True, True)
    sub_font = font(22, True, True)
    for i in range(frames):
        phase = (math.sin((i / frames) * math.tau - math.pi/2) + 1) / 2
        frame = bg_base.copy()
        wash = Image.new("RGBA", frame.size, (39, 0, 52, int(110 + phase*35)))
        frame = Image.alpha_composite(frame, wash)
        d = ImageDraw.Draw(frame)
        tw = text_width(d, cfg["text"], title_font)
        x = (width-tw)//2
        y = 98
        glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((x, y), cfg["text"], font=title_font, fill=(229, 57, 255, int(145+phase*100)))
        glow = glow.filter(ImageFilter.GaussianBlur(14 + int(phase*4)))
        frame = Image.alpha_composite(frame, glow)
        d = ImageDraw.Draw(frame)
        d.text((x, y), cfg["text"], font=title_font, fill=(220, 94, 255, 255))
        sw = text_width(d, cfg["subtext"], sub_font)
        d.text(((width-sw)//2, 206), cfg["subtext"], font=sub_font, fill=(191, 155, 207, 255))
        out.append(frame.convert("RGB"))

    out[0].save(out_path, save_all=True, append_images=out[1:], duration=duration, loop=0, optimize=False, disposal=2)
    return out[0]


def save_png(img, path):
    img.convert("RGB").save(path, optimize=False)


def build_index(section_names):
    blocks = "\n".join(f'    <img src="{name}" alt="Rogue Assembly faction section">' for name in section_names)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Rogue Assembly — Faction Description</title>
  <style>
    html,body{{margin:0;background:#050308;color:#fff;font-family:Arial,sans-serif;}}
    main{{max-width:1000px;margin:0 auto;line-height:0;}}
    img{{display:block;width:100%;height:auto;margin:0;border:0;}}
  </style>
</head>
<body><main>
{blocks}
</main></body>
</html>
"""


def build():
    cfg = load_config()
    width = int(cfg.get("canvas_width", 1000))
    DOCS.mkdir(parents=True, exist_ok=True)

    hero_source = load_image(cfg["assets"]["hero"])
    recruiting = render_recruiting(cfg["recruiting"], hero_source, width)
    hero = render_hero(hero_source, width)
    about = render_about(cfg["about"], width)
    rogue = render_rogue_code(cfg["rogue_code"], width)
    footer_first = render_footer_gif(cfg["footer"], hero_source, DOCS / "footer.gif", width)

    save_png(recruiting, DOCS / "recruiting.png")
    save_png(hero, DOCS / "hero.png")
    save_png(about, DOCS / "about.png")
    save_png(rogue, DOCS / "rogue-code.png")

    parts = [recruiting.convert("RGBA"), hero.convert("RGBA"), about, rogue, footer_first.convert("RGBA")]
    preview = Image.new("RGBA", (width, sum(p.height for p in parts)), BLACK)
    y = 0
    for part in parts:
        preview.alpha_composite(part, (0, y))
        y += part.height
    save_png(preview, DOCS / "full-preview.png")

    section_names = ["recruiting.png", "hero.png", "about.png", "rogue-code.png", "footer.gif"]
    (DOCS / "index.html").write_text(build_index(section_names), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    base = "https://purplezyn.github.io/faction-description"
    snippet = "\n".join(f'<p><img src="{base}/{name}"></p>' for name in section_names)
    (DOCS / "torn-embed-snippet.html").write_text(snippet + "\n", encoding="utf-8")

    print("Built Rogue Assembly faction description")
    for name in section_names + ["full-preview.png"]:
        p = DOCS / name
        print(f" - {name}: {p.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
