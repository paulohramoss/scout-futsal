#!/usr/bin/env python3
"""Gera os icones do app (tela de inicio do iPad / Android).

Marca: quadra de futsal vista de cima, nas cores do app (verde --accent).
Roda so quando o icone muda: `python3 make-icons.py`
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "icons")

BG = (10, 18, 20)        # --paper escuro
FG = (25, 169, 143)      # --accent escuro
LINE = (230, 236, 234)   # --ink escuro


def draw(size):
    # desenha 4x maior e reduz: vira antialiasing de pobre, mas funciona
    s = size * 4
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)

    pad = s * 0.14
    w = s - 2 * pad
    h = w * 0.5
    top = (s - h) / 2
    box = [pad, top, pad + w, top + h]
    lw = max(2, int(s * 0.012))

    d.rectangle(box, outline=FG, width=lw)
    d.line([s / 2, top, s / 2, top + h], fill=FG, width=lw)
    r = h * 0.26
    d.ellipse([s / 2 - r, top + h / 2 - r, s / 2 + r, top + h / 2 + r],
              outline=FG, width=lw)

    # areas: meio circulo de cada lado
    ar = h * 0.55
    d.arc([pad - ar, top + h / 2 - ar, pad + ar, top + h / 2 + ar],
          -90, 90, fill=FG, width=lw)
    d.arc([pad + w - ar, top + h / 2 - ar, pad + w + ar, top + h / 2 + ar],
          90, 270, fill=FG, width=lw)

    # bola no centro
    br = s * 0.045
    d.ellipse([s / 2 - br, top + h / 2 - br, s / 2 + br, top + h / 2 + br],
              fill=LINE)

    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(ICONS, exist_ok=True)
    for size in (180, 192, 512):
        p = os.path.join(ICONS, "icon-%d.png" % size)
        draw(size).save(p, optimize=True)
        print("gerado:", p)


if __name__ == "__main__":
    main()
