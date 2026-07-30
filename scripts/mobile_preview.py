#!/usr/bin/env python3
"""Génère des aperçus (captures) de l'app mobile DressIT.

Reproduit fidèlement les écrans React Native (mêmes couleurs `src/theme.js`,
mêmes mises en page) dans un cadre de téléphone, avec les vrais articles de la
boutique, puis prend une capture d'écran via Playwright (Chromium).

Usage :  python scripts/mobile_preview.py
Sortie :  media/mobile_preview/dressit-mobile.png
"""

import base64
import os
import sys
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dressit.settings")
django.setup()

from django.conf import settings  # noqa: E402
from store.models import Product  # noqa: E402

# --- Palette identique à mobile/src/theme.js ---
C = {
    "bg": "#17130e", "bgAlt": "#1c1610", "surface": "#241c15", "surface2": "#2f251b",
    "border": "#43331f", "text": "#f9f5ee", "textSoft": "#d6c6ac", "textMuted": "#a3907a",
    "gold": "#e0bd6a", "brownDark": "#2f221a",
}


def money(v):
    n = int(round(float(v or 0)))
    s = f"{n:,}".replace(",", " ")
    return f"{s} FCFA"


def data_uri(field):
    try:
        p = Path(field.path)
        raw = p.read_bytes()
        ext = p.suffix.lower().lstrip(".") or "jpeg"
        ext = "jpeg" if ext == "jpg" else ext
        return f"data:image/{ext};base64," + base64.b64encode(raw).decode()
    except Exception:
        return None


products = list(
    Product.objects.filter(is_active=True).prefetch_related("images", "sizes", "colors")[:6]
)
imgs = {}
for p in products:
    im = p.images.first()
    imgs[p.id] = data_uri(im.image) if im else None


def thumb(p):
    src = imgs.get(p.id)
    inner = f'<img src="{src}">' if src else '<span class="noph">👗</span>'
    badge = ""
    if p.is_on_sale:
        badge = f'<span class="badge">-{p.discount_percent}%</span>'
    elif not p.in_stock:
        badge = '<span class="badge out">Épuisé</span>'
    old = f'<span class="old">{money(p.compare_at_price)}</span>' if p.is_on_sale else ""
    return f"""
    <div class="card">
      <div class="thumb">{inner}{badge}</div>
      <div class="cinfo">
        <div class="cat">{p.category.name}</div>
        <div class="cname">{p.name}</div>
        <div class="prow"><span class="price">{money(p.price)}</span>{old}</div>
      </div>
    </div>"""


# ---- Écran 1 : Boutique (grille) ----
grid = "".join(thumb(p) for p in products)
screen_shop = f"""
<div class="statusbar"><span>9:41</span><span>􀙇 􀛨 100%</span></div>
<div class="navbar">DressIT</div>
<div class="searchrow">
  <div class="search">Rechercher un article…</div>
  <div class="searchbtn">🔎</div>
</div>
<div class="tabs">
  <div class="tab active">Tout</div><div class="tab">Femme</div><div class="tab">Homme</div>
</div>
<div class="grid">{grid}</div>
"""

# ---- Écran 2 : Détail article ----
p = products[0]
hero = f'<img src="{imgs.get(p.id)}">' if imgs.get(p.id) else '<span class="noph big">👗</span>'
sizes = "".join(
    f'<div class="pill {"on" if i == 1 else ""}">{s.label}</div>'
    for i, s in enumerate(p.sizes.all()[:5])
)
colors_html = "".join(
    f'<div class="pill {"on" if i == 0 else ""}"><span class="dot" style="background:{c.hex_code}"></span>{c.name}</div>'
    for i, c in enumerate(p.colors.all()[:4])
)
desc = (p.description or "Pièce élégante aux finitions soignées, dans l'esprit chaleureux de DressIT.")[:180]
screen_detail = f"""
<div class="statusbar"><span>9:41</span><span>􀙇 􀛨 100%</span></div>
<div class="navbar"><span class="back">‹</span> DressIT</div>
<div class="detail">
  <div class="hero">{hero}</div>
  <div class="dbody">
    <div class="dcat">{p.category.name} · {p.get_gender_display()}</div>
    <div class="dname">{p.name}</div>
    <div class="prow"><span class="dprice">{money(p.price)}</span></div>
    <div class="dlabel">Taille</div>
    <div class="pills">{sizes}</div>
    <div class="dlabel">Couleur</div>
    <div class="pills">{colors_html}</div>
    <div class="ddesc">{desc}</div>
    <div class="addbtn">🛍️&nbsp; Ajouter au panier</div>
  </div>
</div>
"""

# ---- Écran 3 : Panier ----
cart_items = products[1:4]
rows = ""
total = 0
for it in cart_items:
    total += int(it.price)
    src = imgs.get(it.id)
    im = f'<img src="{src}">' if src else '<span class="noph">👗</span>'
    rows += f"""
    <div class="crow">
      <div class="cthumb">{im}</div>
      <div class="cmid">
        <div class="cn">{it.name}</div>
        <div class="cv">M · {it.colors.first().name if it.colors.exists() else '—'}</div>
        <div class="cp">{money(it.price)}</div>
      </div>
      <div class="qty">−&nbsp;1&nbsp;+</div>
    </div>"""
ship = 2000
screen_cart = f"""
<div class="statusbar"><span>9:41</span><span>􀙇 􀛨 100%</span></div>
<div class="navbar">Panier</div>
<div class="cart">
  {rows}
  <div class="sumbox">
    <div class="sl"><span>Sous-total</span><span>{money(total)}</span></div>
    <div class="sl"><span>Livraison</span><span>{money(ship)}</span></div>
    <div class="sl tot"><span>Total</span><span class="gold">{money(total + ship)}</span></div>
  </div>
  <div class="addbtn">Passer la commande →</div>
</div>
"""


def tabbar(active):
    items = [("🛍️", "Boutique"), ("📷", "Photo"), ("🛒", "Panier"), ("👤", "Compte")]
    cells = ""
    for emoji, label in items:
        cls = "tbi on" if label == active else "tbi"
        badge = '<span class="tbadge">3</span>' if label == "Panier" and active != "Panier" else ""
        cells += f'<div class="{cls}"><span class="te">{emoji}{badge}</span><span class="tl">{label}</span></div>'
    return f'<div class="tabbar">{cells}</div>'


phones = f"""
<div class="phone"><div class="screen">{screen_shop}{tabbar("Boutique")}</div><div class="label">Boutique</div></div>
<div class="phone"><div class="screen">{screen_detail}{tabbar("Boutique")}</div><div class="label">Fiche article</div></div>
<div class="phone"><div class="screen">{screen_cart}{tabbar("Panier")}</div><div class="label">Panier</div></div>
"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; margin: 0; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; }}
body {{ background: #0e0b07; padding: 40px; }}
.wrap {{ display: flex; gap: 40px; justify-content: center; align-items: flex-start; }}
.phone {{ text-align: center; }}
.screen {{
  width: 300px; height: 640px; background: {C['bg']}; border-radius: 34px;
  border: 10px solid #000; overflow: hidden; position: relative; box-shadow: 0 24px 60px #000a;
  display: flex; flex-direction: column;
}}
.label {{ color: {C['gold']}; margin-top: 16px; font-weight: 700; letter-spacing: .5px; }}
.statusbar {{ display: flex; justify-content: space-between; padding: 8px 18px 4px; color: {C['text']}; font-size: 12px; font-weight: 600; }}
.navbar {{ background: {C['brownDark']}; color: #fff; text-align: center; padding: 12px; font-weight: 700; font-size: 16px; position: relative; }}
.navbar .back {{ position: absolute; left: 14px; font-size: 22px; top: 6px; }}
.searchrow {{ display: flex; gap: 8px; padding: 12px; }}
.search {{ flex: 1; background: {C['surface2']}; border: 1px solid {C['border']}; border-radius: 24px; padding: 9px 16px; color: {C['textMuted']}; font-size: 13px; }}
.searchbtn {{ background: {C['gold']}; border-radius: 24px; padding: 9px 14px; }}
.tabs {{ display: flex; gap: 8px; padding: 0 12px 8px; }}
.tab {{ padding: 7px 15px; border-radius: 20px; background: {C['surface2']}; border: 1px solid {C['border']}; color: {C['textSoft']}; font-size: 13px; font-weight: 600; }}
.tab.active {{ background: {C['gold']}; border-color: {C['gold']}; color: #2a1d0c; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 0 10px; overflow: hidden; flex: 1; }}
.card {{ background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 14px; overflow: hidden; }}
.thumb {{ position: relative; aspect-ratio: .8; background: {C['surface2']}; display: flex; align-items: center; justify-content: center; }}
.thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
.noph {{ font-size: 34px; }}
.noph.big {{ font-size: 70px; }}
.badge {{ position: absolute; top: 7px; left: 7px; background: {C['gold']}; color: #2a1d0c; font-weight: 700; font-size: 10px; padding: 3px 7px; border-radius: 10px; }}
.badge.out {{ background: #6b6b6b; color: #fff; }}
.cinfo {{ padding: 8px 9px 10px; }}
.cat {{ color: {C['textMuted']}; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }}
.cname {{ color: {C['text']}; font-weight: 600; font-size: 12px; margin-top: 2px; line-height: 1.25; }}
.prow {{ display: flex; align-items: center; gap: 8px; margin-top: 5px; }}
.price {{ color: {C['gold']}; font-weight: 700; font-size: 13px; }}
.old {{ color: {C['textMuted']}; text-decoration: line-through; font-size: 11px; }}
/* détail */
.detail {{ flex: 1; overflow: hidden; }}
.hero {{ aspect-ratio: .85; background: {C['surface2']}; display: flex; align-items: center; justify-content: center; }}
.hero img {{ width: 100%; height: 100%; object-fit: cover; }}
.dbody {{ padding: 14px 16px; }}
.dcat {{ color: {C['textMuted']}; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}
.dname {{ color: {C['text']}; font-size: 19px; font-weight: 700; margin: 5px 0; }}
.dprice {{ color: {C['gold']}; font-size: 19px; font-weight: 700; }}
.dlabel {{ color: {C['textSoft']}; font-weight: 600; margin: 14px 0 7px; font-size: 13px; }}
.pills {{ display: flex; flex-wrap: wrap; gap: 7px; }}
.pill {{ display: flex; align-items: center; gap: 5px; padding: 6px 12px; border-radius: 18px; border: 1px solid {C['border']}; background: {C['surface']}; color: {C['text']}; font-size: 12px; }}
.pill.on {{ background: {C['gold']}; border-color: {C['gold']}; color: #2a1d0c; font-weight: 700; }}
.dot {{ width: 12px; height: 12px; border-radius: 50%; border: 1px solid #0004; }}
.ddesc {{ color: {C['textSoft']}; margin-top: 14px; line-height: 1.5; font-size: 12px; }}
.addbtn {{ background: {C['gold']}; color: #2a1d0c; font-weight: 700; text-align: center; padding: 13px; border-radius: 26px; margin-top: 16px; font-size: 14px; }}
/* panier */
.cart {{ flex: 1; padding: 12px; overflow: hidden; }}
.crow {{ display: flex; gap: 10px; background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 12px; padding: 8px; margin-bottom: 10px; }}
.cthumb {{ width: 56px; height: 66px; border-radius: 8px; overflow: hidden; background: {C['surface2']}; display: flex; align-items: center; justify-content: center; flex: none; }}
.cthumb img {{ width: 100%; height: 100%; object-fit: cover; }}
.cmid {{ flex: 1; }}
.cn {{ color: {C['text']}; font-weight: 600; font-size: 13px; }}
.cv {{ color: {C['textMuted']}; font-size: 11px; margin: 3px 0; }}
.cp {{ color: {C['gold']}; font-weight: 700; font-size: 13px; }}
.qty {{ color: {C['textSoft']}; font-size: 12px; align-self: center; border: 1px solid {C['border']}; border-radius: 16px; padding: 5px 9px; white-space: nowrap; }}
.sumbox {{ background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 12px; padding: 12px; margin-top: 4px; }}
.sl {{ display: flex; justify-content: space-between; color: {C['textSoft']}; font-size: 13px; padding: 5px 0; }}
.sl.tot {{ border-top: 1px dashed {C['border']}; margin-top: 6px; padding-top: 10px; font-size: 16px; font-weight: 700; color: {C['text']}; }}
.gold {{ color: {C['gold']}; }}
/* barre d'onglets */
.tabbar {{ display: flex; background: {C['brownDark']}; border-top: 1px solid {C['border']}; margin-top: auto; }}
.tbi {{ flex: 1; text-align: center; padding: 8px 0 10px; color: {C['textMuted']}; }}
.tbi.on {{ color: {C['gold']}; }}
.te {{ display: block; font-size: 18px; position: relative; }}
.tbi.on .te {{ font-size: 21px; }}
.tl {{ font-size: 10px; margin-top: 2px; display: block; }}
.tbadge {{ position: absolute; top: -4px; right: 50%; margin-right: -18px; background: {C['gold']}; color: #2a1d0c; font-size: 9px; font-weight: 700; border-radius: 8px; padding: 0 5px; }}
</style></head><body><div class="wrap">{phones}</div></body></html>"""

out_dir = Path(settings.MEDIA_ROOT) / "mobile_preview"
out_dir.mkdir(parents=True, exist_ok=True)
html_path = out_dir / "preview.html"
html_path.write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright  # noqa: E402

png_path = out_dir / "dressit-mobile.png"
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        args=["--no-sandbox"],
    )
    page = browser.new_page(viewport={"width": 1120, "height": 780}, device_scale_factor=2)
    page.goto(html_path.as_uri())
    page.wait_for_timeout(400)
    page.locator(".wrap").screenshot(path=str(png_path))
    browser.close()

print("OK ->", png_path)
