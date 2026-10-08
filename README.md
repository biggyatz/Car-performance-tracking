# Car Performance Tracking

Predicts a car's fuel efficiency (**miles per gallon**) from its engine and
body specs with a Random Forest regressor, served through a Flask web app.
Built during the SmartInternz applied data science internship.

| Model (test set) | RMSE |
| --- | --- |
| **Random Forest Regressor** (deployed) | **2.90** |
| Multiple Linear Regression | 3.49 |
| K-Neighbours Regressor | 4.43 |
| Support Vector Regressor | 5.21 |

Random Forest: R² = 0.854, MAE = 2.08 mpg.

## Inputs

`cylinders`, `displacement` (cu in), `horsepower`, `weight` (lb),
`acceleration` (0–60 s), `model year` (e.g. 70 for 1970), `origin`
(1 = USA, 2 = Europe, 3 = Japan). Data: the classic Auto MPG dataset
(`dataset.csv`).

## Project layout

| Path | What it is |
| --- | --- |
| `app.py` | Flask app: form (`/`), prediction (`/Result`), health check (`/health`) |
| `model.pkl` | Trained `RandomForestRegressor` (scikit-learn 1.0.2) |
| `notebooks/Car_Performance_Prediction.ipynb` | EDA, model comparison, training |
| `templates/finalweb.html` | Input form |
| `dataset.csv` | Auto MPG data |
| `Dockerfile`, `render.yaml`, `Procfile` | Deployment config |

## Run locally

`model.pkl` was saved with scikit-learn 1.0.2, which needs **Python 3.10 or older**.

```bash
python3.10 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py                          # http://localhost:5000
```

Or with Docker (handles the Python version for you):

```bash
docker build -t car-performance .
docker run -p 8000:8000 car-performance   # http://localhost:8000
```

## Deploy

The original Heroku + GitHub Actions pipeline stopped working when Heroku
dropped its free tier. It now deploys on **Render's free plan**:

1. Sign in at <https://dashboard.render.com> with GitHub.
2. **New → Blueprint** → select this repository → **Apply**.

Free Render services sleep after 15 minutes idle (first request ~30–60 s).

## Security note

An IBM Cloud API key (`apikey.json`) used to be committed to this repository.
The file is removed and git-ignored, but it is still in the git history, so
**revoke that key** in IBM Cloud → Manage → Access (IAM) → API keys.
