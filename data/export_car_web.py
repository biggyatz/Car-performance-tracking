"""Write web/model.json and web/listings.json for the car app."""
import json, re, sys
import pandas as pd
out = sys.argv[1]
model = json.load(open("car_model.json"))
df = pd.read_csv("car_model_rows.csv")
rows = [{"title": r.title[:90], "make": r.make, "family": r.family, "year": int(r.year), "condition": r.condition if isinstance(r.condition, str) else None,
         "price": int(r.price_npr), "km": None if pd.isna(r.km) else int(r.km), "url": r.url} for r in df.itertuples()]
json.dump(model, open(f"{out}/model.json", "w"), separators=(",", ":"))
json.dump(rows, open(f"{out}/listings.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("car model + listings", len(rows))
