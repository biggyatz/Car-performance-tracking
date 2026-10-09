# Nepal Used Car Value Estimator

**Live app:** <https://biggyatz.github.io/Car-performance-tracking/web/>

Estimate what a used car is worth in Nepal from **422 real listings** across **68 models**. Pick the make, model, year and (optionally) kilometres. You get an estimated market value with a likely range, today's showroom price for that model with the share of value retained, a value-by-year curve plotted against real asking prices, similar cars currently for sale, and Nepal's typical depreciation curve.

The app is a static page on GitHub Pages: the model runs in the browser, with no server and no cost.

> This repository started as the SmartInternz car-performance (mpg) project. That original work, including the certificate, is preserved in [`legacy-auto-mpg/`](legacy-auto-mpg/).

## Data

| Source | What | Count | How it was collected |
| --- | --- | --- | --- |
| [hamrobazaar.com](https://hamrobazaar.com) | Used-car asking prices | 422 after cleaning | Search and listing pages (`/search/product`, `/detail/`, allowed in `robots.txt`) |
| [nepaldrives.com](https://www.nepaldrives.com) | New-car prices (2026 guides) | 128 models, 25 brands | Brand price pages (allowed in `robots.txt`) |

* Collected in October 2026, rate-limited.
* Only car attributes are kept (title, price, make year, km, fuel or transmission keywords, URL); phone numbers and seller names are removed.
* [EV News Nepal](https://evnewsnepal.com) asks for permission before bulk reuse, so its catalogue was not used.
* Prices are **asking prices**, not dealer quotes or bank valuations.

Cleaning (`data/clean_cars.py`):
* Free-text titles are mapped to a make and model family with ordered patterns (Grand i10 before i10, Dzire before Swift, Nexon EV before Nexon).
* Bikram Sambat model years (e.g. 2075) are converted to AD.
* Rentals, parts and accessories are dropped, along with prices outside Rs 2 lakh – 3 crore.
* Seller-chosen condition labels ("Brand new" on decade-old cars) proved unreliable and are ignored.

## Model

A regression on log(price) with ridge regularisation:

`log(price) = make + model family + age + age² + log(km) + electric × age`

Model families with at least 3 listings get their own effect, shrunk toward the make; rarer models fall back to the make. Listings more than ~2.5× off the fitted value are treated as data errors (one robust pass).

| 5-fold cross-validation | Ridge (deployed) | Gradient boosting |
| --- | --- | --- |
| R² (log price) | 0.915 | 0.665 |
| Median absolute error | 7.7% | 13.5% |
| Within ±20% | 85.1% | 62.8% |

`web/predict.js` reproduces the Python model exactly (max relative difference ~1e-15). Most-listed models: Hyundai i10 (37), Hyundai i20 (27), Hyundai Creta (24), Hyundai Santro (24), Suzuki Swift (23), Hyundai Grand i10 (22), Ford EcoSport (14), Hyundai Eon (11).

## Repository layout

| Path | What it is |
| --- | --- |
| `web/` | The app: `index.html`, `app.js`, `predict.js`, `style.css`, plus `model.json` and `listings.json` |
| `index.html` | Redirects the Pages root to `web/` (this repo's Pages site builds from `main`) |
| `data/crawl_hamrobazar*.js`, `data/crawl_nepaldrives.py` | Polite crawlers |
| `data/clean_cars.py`, `data/nepal_units.py` | Title → model mapping, year/price parsing |
| `data/train_car_model.py`, `data/export_car_web.py` | Training, cross-validation, export |
| `data/car_listings.csv`, `data/new_car_prices.json` | Cleaned datasets |
| `legacy-auto-mpg/` | The original SmartInternz mpg project (Flask, Docker, notebook, certificate) |

## Refreshing the data

```bash
cd data
node crawl_hamrobazar.js '/detail/cars/' raw_hamrobazar_cars.jsonl "hyundai i10" "suzuki swift" ...
node crawl_hamrobazar_details.js raw_hamrobazar_cars.jsonl raw_hamrobazar_car_details.jsonl
python crawl_nepaldrives.py
python clean_cars.py && python train_car_model.py && python export_car_web.py ../web
```

## Security note

An IBM Cloud API key (`apikey.json`) was committed in this repository's early history. Revoke it in IBM Cloud → Manage → Access (IAM) → API keys.
