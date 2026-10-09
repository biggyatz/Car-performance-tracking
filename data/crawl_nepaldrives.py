"""Fetch NepalDrives brand price pages (robots.txt allows) and extract MODEL/PRICE tables."""
import html, json, re, time, urllib.request, sys
BRANDS = """toyota hyundai kia tata mahindra suzuki honda nissan mg byd ford volkswagen skoda renault jeep isuzu
mitsubishi subaru mercedes-benz mercedes bmw audi peugeot citroen haval gwm changan dongfeng proton deepal neta jmev
chery jetour geely ora tesla seres xpeng zeekr leapmotor wuling kaiyi vinfast mini lexus land-rover volvo great-wall
mg-cars dfsk foton kyc baic jac omoda jaecoo avatr aion gac riddara skywell yuan""".split()
UA = {"User-Agent": "Mozilla/5.0 (research crawler; contact via github.com/biggyatz)"}
def get(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    except Exception:
        return None
out = []
for b in BRANDS:
    for suffix in ("-car-price-in-nepal-latest", "-car-price-in-nepal", "-cars-price-in-nepal-latest", "-price-in-nepal"):
        url = f"https://www.nepaldrives.com/{b}{suffix}"
        page = get(url); time.sleep(1.0)
        if not page:
            continue
        rows = []
        for tb in re.findall(r"<table.*?</table>", page, re.S):
            for r in re.findall(r"<tr.*?</tr>", tb, re.S):
                cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"<t[dh].*?</t[dh]>", r, re.S)]
                if len(cells) >= 2 and re.search(r"(?i)rs\.?\s*[\d.,]+\s*(lakh|crore|lac)", cells[-1]):
                    rows.append(cells)
        if rows:
            m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', page) or re.search(r'(?i)published[^<]{0,40}?(\d{4}-\d{2}-\d{2})', page)
            m2 = re.search(r'"dateModified"\s*:\s*"([^"]+)"', page)
            out.append({"brand": b, "url": url, "published": m.group(1) if m else None, "modified": m2.group(1) if m2 else None, "rows": rows})
            print(b, len(rows), url, file=sys.stderr)
            break
json.dump(out, open("raw_nepaldrives.json", "w"), ensure_ascii=False, indent=1)
print("brands found", len(out), "models", sum(len(o["rows"]) for o in out))
