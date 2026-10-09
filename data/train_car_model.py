"""Used-car value model for Nepal (Hamrobazar asking prices) -> car_model.json.

log(price) = make + family (ridge-shrunk) + age + age^2 + log(km) + EV
"""
import json, re
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold, cross_val_predict

NOW = 2026
df = pd.read_csv("cars.csv").dropna(subset=["year"])
df = df[(df.year >= 1990) & (df.year <= NOW)].copy()
df["age"] = (NOW - df.year).clip(0, 35)
df["ev"] = (df.family.str.contains(r"EV|Atto|Dolphin|Seal|Neta|e2o|Kona|Ioniq|Deepal", regex=True) | df.fuel.fillna("").str.contains("elec|EV", case=False)).astype(float)
df["condition"] = df.condition.fillna("Used")
# Remove gross outliers per family (wrong units, typos): >3x from family-age trend median.
df["lp"] = np.log(df.price_npr)
fam_counts = df.family.value_counts()
MIN_FAM = 3
df["fam"] = np.where(df.family.isin(fam_counts[fam_counts >= MIN_FAM].index), df.make + " " + df.family, "")

def design(d, cols=None):
    X = pd.DataFrame(index=d.index)
    X["age"] = d.age; X["age2"] = d.age ** 2 / 10
    X["ev"] = d.ev; X["ev_age"] = d.ev * d.age
    km = d.km.clip(1000, 300000) if "km" in d else pd.Series(np.nan, index=d.index)
    X["km_missing"] = km.isna().astype(float); X["log_km"] = np.log(km.fillna(60000)) - np.log(60000)
    # Hamrobazar condition labels ("Brand new" on 10-year-old cars) are unreliable, so condition is not used.
    for v in sorted(d.make.unique()): X["m=" + v] = (d.make == v).astype(float)
    for v in sorted(set(d.fam) - {""}): X["f=" + v] = (d.fam == v).astype(float)
    return X if cols is None else X.reindex(columns=cols, fill_value=0.0)

X, y = design(df), df.lp.values
# One robust pass: fit, drop listings > 0.9 log-points off (≈2.5x), refit.
cv = KFold(5, shuffle=True, random_state=42)
ridge = RidgeCV(alphas=np.logspace(-2, 2, 20)).fit(X, y)
keep = np.abs(y - ridge.predict(X)) < 0.9
df, X, y = df[keep].copy(), X[keep], y[keep]
p_lin = cross_val_predict(RidgeCV(alphas=np.logspace(-2, 2, 20)), X, y, cv=cv)
p_gb = cross_val_predict(HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, min_samples_leaf=10, random_state=0), X, y, cv=cv)
def report(p):
    err = np.exp(p - y) - 1
    return {"r2_log": round(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum(), 3),
            "median_abs_pct_err": round(float(np.median(np.abs(err))) * 100, 1),
            "within_20pct": round(float((np.abs(err) < 0.20).mean()) * 100, 1)}
print("rows", len(df), "dropped outliers", int((~keep).sum()), "features", X.shape[1])
print("ridge", report(p_lin)); print("gboost", report(p_gb))
ridge = RidgeCV(alphas=np.logspace(-2, 2, 20)).fit(X, y)
resid = y - p_lin
new = json.load(open("new_car_prices.json"))
def new_price(make, fam):
    cands = [r for r in new if r["brand"].lower().startswith(make.lower()[:3]) and fam.lower().replace("-", " ") in r["model"].lower().replace("-", " ")]
    cands.sort(key=lambda r: len(r["model"]))
    return {"model": cands[0]["model"], "low": cands[0]["price_low"], "high": cands[0]["price_high"], "url": cands[0]["source_url"]} if cands else None
families = []
for (make, fam), g in df.groupby(["make", "family"]):
    families.append({"make": make, "family": fam, "n": int(len(g)), "pooled": (make + " " + fam) not in set(df.fam),
                     "year_min": int(g.year.min()), "year_max": int(g.year.max()), "new": new_price(make, fam), "ev": bool(g.ev.max())})
model = {"intercept": float(ridge.intercept_), "coef": dict(zip(X.columns, ridge.coef_.tolist())), "alpha": float(ridge.alpha_), "now": NOW,
         "resid_q": {q: float(np.quantile(resid, q)) for q in (0.1, 0.25, 0.75, 0.9)},
         "cv": report(p_lin), "cv_gboost": report(p_gb), "n": int(len(df)), "families": families,
         "km_share": round(float(df.km.notna().mean()), 3)}
json.dump(model, open("car_model.json", "w"), indent=1)
df.to_csv("car_model_rows.csv", index=False)
print("alpha", ridge.alpha_, "families", len(families), "with new price", sum(f["new"] is not None for f in families))
print({k: round(v, 3) for k, v in model["coef"].items() if not k.startswith(("m=", "f="))})
