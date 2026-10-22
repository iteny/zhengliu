#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch Aozora Bunko texts for Edogawa Ranpo and normalize to plain UTF-8 text."""
import os, re, sys, time, urllib.request, html

UA = {"User-Agent": "Mozilla/5.0 (research; text-mining for academic style analysis)"}
BASE = "https://www.aozora.gr.jp/cards/001779/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "txt")
os.makedirs(OUT, exist_ok=True)

# card_id : slug
WORKS = {
    "56647": "01_nisen_douka",        # 二銭銅貨 1923
    "56650": "02_dsaka",             # D坂の殺人事件 1925
    "56649": "03_yaneura",           # 屋根裏の散歩者 1925
    "56648": "04_ningen_isu",        # 人間椅子 1925
    "57503": "05_injuu",             # 陰獣 1928
    "57405": "06_kurotokage",        # 黒蜥蜴 1934
    "57228": "07_kaijin20_a",        # 怪人二十面相 (1936)
    "56669": "08_shounen_tanteidan", # 少年探偵団 1937
    "56651": "09_panorama",          # パノラマ島綺譚 1926
    "56645": "10_oshie",             # 押絵と旅する男 1929
    "57506": "11_kasei_no_unga",     # 火星の運河 1926
    "57181": "12_akai_heya",         # 赤い部屋 1925
    "56646": "13_shinri_shiken",     # 心理試験 1925
    "57187": "14_souseiji",          # 双生児 1924
    "57511": "15_hitodenashi",       # 人でなしの恋 1926
    "57343": "16_kagami_jigoku",     # 鏡地獄 1926
    "57245": "17_mushi",             # 虫 1929
    "57105": "18_akai_kabutomushi",  # 赤いカブトムシ 1929
    "57240": "19_akuma_no_monshou",  # 悪魔の紋章 1930
    "58462": "20_dangai",            # 断崖 1950
}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

def clean(raw):
    t = raw.decode("shift_jis", errors="replace")
    # drop ruby annotations: <ruby><rb>漢字</rb><rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>
    t = re.sub(r"<rp>.*?</rp>", "", t, flags=re.S)
    t = re.sub(r"<rt>.*?</rt>", "", t, flags=re.S)
    t = re.sub(r"<script.*?</script>", "", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"</(p|div|h1|h2|h3|li)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = t.replace("\u3000", " ")
    lines = [ln.strip() for ln in t.split("\n")]
    out, blank = [], 0
    for ln in lines:
        if ln == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(ln)
    return "\n".join(out).strip() + "\n"

def main():
    for cid, slug in WORKS.items():
        dst = os.path.join(OUT, slug + ".txt")
        if os.path.exists(dst) and os.path.getsize(dst) > 500:
            print("skip", slug); continue
        try:
            card = get(BASE + "card%s.html" % cid).decode("shift_jis", errors="replace")
            m = re.findall(r'files/(\d+_\d+\.html)', card)
            if not m:
                print("NO FILE", cid, slug); continue
            body = get(BASE + "files/" + m[0])
            txt = clean(body)
            with open(dst, "w", encoding="utf-8") as f:
                f.write(txt)
            print("ok", slug, len(txt), m[0])
            time.sleep(1.2)
        except Exception as e:
            print("ERR", slug, type(e).__name__, e)

if __name__ == "__main__":
    main()
