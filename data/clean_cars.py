"""Clean Hamrobazar car listings into cars.csv (make, family, year, condition, km, price)."""
import json, os, re
import pandas as pd
from nepal_units import ad_year, strip_phones

# (make, family, regex) - order matters: specific before general.
FAMILIES = [
    ("Hyundai", "Grand i10", r"grand\s*i\s*-?10|i10\s*grand|nios"), ("Hyundai", "i10", r"\bi\s*-?10\b"),
    ("Hyundai", "i20", r"\bi\s*-?20\b"), ("Hyundai", "Santro", r"santro"), ("Hyundai", "Creta", r"creta"),
    ("Hyundai", "Venue", r"venue"), ("Hyundai", "Verna", r"verna"), ("Hyundai", "Tucson", r"tucson"),
    ("Hyundai", "Accent", r"accent"), ("Hyundai", "Eon", r"\beon\b"), ("Hyundai", "Getz", r"getz|gezt"), ("Hyundai", "Kona", r"kona"),
    ("Hyundai", "Xcent", r"xcent"), ("Hyundai", "Aura", r"\baura\b"), ("Hyundai", "Exter", r"exter"), ("Hyundai", "Ioniq", r"ioniq"),
    ("Suzuki", "Alto", r"\balto\b"), ("Suzuki", "Dzire", r"d\s*zire|dizar|dezire|desire"), ("Suzuki", "Swift", r"swift"),
    ("Suzuki", "Wagon R", r"wagon\s*-?\s*r|wagonr"), ("Suzuki", "Celerio", r"celerio"), ("Suzuki", "Baleno", r"baleno"),
    ("Suzuki", "Ertiga", r"ertiga"), ("Suzuki", "Brezza", r"brezza"), ("Suzuki", "Grand Vitara", r"vitara"),
    ("Suzuki", "Ciaz", r"ciaz"), ("Suzuki", "Zen Estilo", r"estilo|\bzen\b"), ("Suzuki", "S-Presso", r"s\s*-?\s*presso"),
    ("Suzuki", "800", r"maruti\s*800|\b800\b"), ("Suzuki", "Ritz", r"\britz\b"), ("Suzuki", "A-Star", r"a\s*-?\s*star"),
    ("Suzuki", "Ignis", r"ignis"), ("Suzuki", "Fronx", r"fronx"), ("Suzuki", "Jimny", r"jimny"),
    ("Toyota", "Corolla", r"corolla"), ("Toyota", "Yaris", r"yaris"), ("Toyota", "Fortuner", r"fortuner"),
    ("Toyota", "Prado", r"prado"), ("Toyota", "Land Cruiser", r"land\s*cruiser"), ("Toyota", "RAV4", r"rav\s*-?4"),
    ("Toyota", "Hilux", r"hilux"), ("Toyota", "Vitz", r"vitz"), ("Toyota", "Etios", r"etios"), ("Toyota", "Innova", r"innova"),
    ("Toyota", "Raize", r"raize"), ("Toyota", "Glanza", r"glanza"),
    ("Kia", "Picanto", r"picanto|\bmorning\b"), ("Kia", "Rio", r"\brio\b"), ("Kia", "Seltos", r"seltos"), ("Kia", "Sonet", r"sonet"),
    ("Kia", "Sportage", r"sportage"), ("Kia", "Sorento", r"sorento"), ("Kia", "EV6", r"\bev\s*6\b"), ("Kia", "Niro", r"niro"),
    ("Tata", "Nexon EV", r"nexon\s*ev|nexon.*electric"), ("Tata", "Nexon", r"nexon"), ("Tata", "Tiago", r"tiago"),
    ("Tata", "Tigor", r"tigor"), ("Tata", "Indica", r"indica|vista"), ("Tata", "Nano", r"\bnano\b"), ("Tata", "Punch", r"\bpunch\b"),
    ("Tata", "Altroz", r"altroz"), ("Tata", "Safari", r"safari"), ("Tata", "Sumo", r"sumo"), ("Tata", "Indigo", r"indigo"),
    ("Mahindra", "Scorpio", r"scorpio"), ("Mahindra", "Bolero", r"bolero"), ("Mahindra", "XUV", r"\bxuv"), ("Mahindra", "KUV100", r"kuv"),
    ("Mahindra", "Thar", r"\bthar\b"), ("Mahindra", "e2o", r"e2o|reva"),
    ("Honda", "City", r"honda\s*city|\bcity\b"), ("Honda", "Civic", r"civic"), ("Honda", "Jazz", r"\bjazz\b"), ("Honda", "Brio", r"\bbrio\b"),
    ("Honda", "WR-V", r"wr\s*-?\s*v"), ("Honda", "CR-V", r"cr\s*-?\s*v"), ("Honda", "Amaze", r"amaze"),
    ("Nissan", "Sunny", r"sunny"), ("Nissan", "Micra", r"micra"), ("Nissan", "X-Trail", r"x\s*-?\s*trail"), ("Nissan", "Magnite", r"magnite"),
    ("Nissan", "Kicks", r"kicks"), ("Ford", "EcoSport", r"eco\s*sport"), ("Ford", "Figo", r"figo"), ("Ford", "Endeavour", r"endeavou?r"),
    ("Renault", "Kwid", r"kwid"), ("Renault", "Duster", r"duster"), ("Volkswagen", "Polo", r"\bpolo\b"), ("Volkswagen", "Vento", r"vento"),
    ("Skoda", "Rapid", r"rapid"), ("MG", "ZS EV", r"\bzs\b"), ("MG", "Hector", r"hector"), ("MG", "MG4", r"\bmg\s*4\b"),
    ("BYD", "Atto 3", r"atto\s*3|atto3"), ("BYD", "Dolphin", r"dolphin"), ("BYD", "Seal", r"\bseal\b"),
    ("Neta", "Neta V", r"neta"), ("Chevrolet", "Spark", r"spark"), ("Chevrolet", "Beat", r"\bbeat\b"), ("Chevrolet", "Aveo", r"aveo"),
    ("Chevrolet", "Cruze", r"cruze"), ("Chevrolet", "Optra", r"optra"),
    ("Mitsubishi", "Pajero", r"pajero"), ("Mitsubishi", "Lancer", r"lancer"), ("Datsun", "Redi-GO", r"redi\s*-?\s*go"),
    ("Datsun", "GO", r"datsun"), ("Jeep", "Compass", r"compass"), ("Proton", "Proton", r"proton"), ("Changan", "Changan", r"changan"),
    ("Haval", "Haval", r"haval"), ("Dongfeng", "Dongfeng", r"dongfeng"), ("Wuling", "Wuling", r"wuling"), ("Deepal", "Deepal", r"deepal"),
]
COND = r"(Brand new|Like new|Used|Not working)"

def family(title):
    t = (title or "").lower()
    for make, fam, rx in FAMILIES:
        if re.search(rx, t):
            return make, fam
    return None, None

def from_card(r):
    m = re.match(rf"^(.*?){COND}([\d,]+)", r["text"].replace("\n", " "), re.S)
    if not m:
        return None
    return {"title": m.group(1).strip(), "condition": m.group(2), "price": m.group(3), "make_year": None, "posted": None}

def year_from_title(t):
    ys = [int(y) for y in re.findall(r"\b(19[89]\d|20\d\d)\b", t or "")]
    ys = [ad_year(y) for y in ys]
    ys = [y for y in ys if y]
    return ys[0] if ys else None

def km_value(txt):
    if not txt:
        return None
    t = txt.lower().replace(" ", "")
    if t.endswith("k"):
        return float(t[:-1]) * 1000
    v = float(re.sub(r"[,.](?=\d{3})", "", t).replace(",", ""))
    return v if 500 <= v <= 400000 else None

def build():
    cards = {json.loads(l)["url"]: json.loads(l) for l in open("raw_hamrobazar_cars.jsonl")}
    det = {}
    if os.path.exists("raw_hamrobazar_car_details.jsonl"):
        for l in open("raw_hamrobazar_car_details.jsonl"):
            d = json.loads(l); det[d["url"]] = d
    rows = []
    for url, c in cards.items():
        d = det.get(url)
        base = d if d and d.get("title") else from_card(c)
        if not base:
            continue
        price = float(re.sub(r"[^\d]", "", base.get("price") or "") or 0)
        if price and price < 10000:
            price *= 1e5          # "18.5" style lakh shorthand is rare; "1850" means 18.5 lakh? keep only lakh shorthand
        make, fam = family(base["title"])
        year = ad_year(int(d["make_year"])) if d and d.get("make_year") and str(d["make_year"]).isdigit() else year_from_title(base["title"])
        rows.append({"url": url, "title": strip_phones(base["title"]), "make": make, "family": fam, "year": year, "condition": base.get("condition"),
                     "price_npr": price, "km": km_value(d.get("km_text")) if d else None, "fuel": (d or {}).get("fuel"),
                     "transmission": (d or {}).get("transmission"), "body_type": (d or {}).get("body_type"), "has_detail": bool(d)})
    df = pd.DataFrame(rows)
    # Drop rentals, parts, wanted ads and absurd prices.
    bad = df.title.str.contains(r"rent|hire|wanted|buy\b|parts?\b|cover|charger|exchange only|tyre|battery", case=False, regex=True)
    df = df[~bad & df.family.notna() & (df.price_npr >= 2e5) & (df.price_npr <= 3e7)].copy()
    return df

if __name__ == "__main__":
    df = build()
    print(len(df), "usable;", df.year.notna().sum(), "with year;", df.km.notna().sum(), "with km")
    print(df.family.value_counts().head(25).to_dict())
    print(df.sample(10, random_state=2)[["title", "family", "year", "condition", "price_npr"]].to_string())
    df.to_csv("cars.csv", index=False)
