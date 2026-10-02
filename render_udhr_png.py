#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont


def generate_graph_png(output_path):
    width, height = 900, 350
    image = Image.new("RGB", (width, height), color="#1e1e1e")
    draw = ImageDraw.Draw(image)

    # Try loading a default or system font, fallback to default
    try:
        font = ImageFont.truetype("consola.ttf", 16)
        font_bold = ImageFont.truetype("consolab.ttf", 18)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_bold = ImageFont.truetype("arialbd.ttf", 18)
        except Exception:
            font = ImageFont.load_default()
            font_bold = font

    # Draw Anchor Box (Left)
    box1_x1, box1_y1, box1_x2, box1_y2 = 50, 100, 380, 250
    draw.rounded_rectangle(
        [box1_x1, box1_y1, box1_x2, box1_y2],
        radius=8,
        fill="#2b2b2b",
        outline="#ff0000",
        width=3,
    )
    draw.text(
        (box1_x1 + 20, box1_y1 + 20), "ANCHOR: 90655f14", fill="#ff4444", font=font_bold
    )
    draw.text(
        (box1_x1 + 20, box1_y1 + 55), "EXPROPRIATED ASSETS", fill="#ffffff", font=font
    )
    draw.text(
        (box1_x1 + 20, box1_y1 + 85),
        "25,210,256.15 MDL",
        fill="#ffdddd",
        font=font_bold,
    )

    # Draw UDHR Box (Right)
    box2_x1, box2_y1, box2_x2, box2_y2 = 520, 90, 850, 260
    draw.rounded_rectangle(
        [box2_x1, box2_y1, box2_x2, box2_y2],
        radius=8,
        fill="#2b2b2b",
        outline="#00aaff",
        width=3,
    )
    draw.text(
        (box2_x1 + 20, box2_y1 + 15), "UDHR Art. 17.2", fill="#00aaff", font=font_bold
    )
    draw.text(
        (box2_x1 + 20, box2_y1 + 45), "«Никто не должен быть", fill="#ffffff", font=font
    )
    draw.text(
        (box2_x1 + 20, box2_y1 + 70), "произвольно лишен", fill="#ffffff", font=font
    )
    draw.text(
        (box2_x1 + 20, box2_y1 + 95), "своего имущества»", fill="#ffffff", font=font
    )

    # Draw Arrow connecting them
    arrow_start_x, arrow_y = box1_x2, (box1_y1 + box1_y2) // 2
    arrow_end_x = box2_x1

    # Line
    draw.line(
        [(arrow_start_x, arrow_y), (arrow_end_x, arrow_y)], fill="#ff0000", width=4
    )

    # Arrowhead
    arrowhead = [
        (arrow_end_x, arrow_y),
        (arrow_end_x - 15, arrow_y - 8),
        (arrow_end_x - 15, arrow_y + 8),
    ]
    draw.polygon(arrowhead, fill="#ff0000")

    # Label on arrow
    draw.text(
        (arrow_start_x + 35, arrow_y - 30),
        "DIRECT VIOLATION",
        fill="#ff4444",
        font=font_bold,
    )

    image.save(output_path)
    print(f"[+] Rendered graph successfully to {output_path}")


if __name__ == "__main__":
    generate_graph_png(r"H:\ACTOR_DEV_ENV\dag_udhr17.png")
    generate_graph_png(r"H:\ACTOR_DEV_ENV\maceret-case-evidence\dag_udhr17.png")
