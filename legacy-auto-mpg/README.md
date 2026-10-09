# Legacy: Car Performance (mpg) Prediction, SmartInternz (2024)

The original SmartInternz applied data science internship project: a 250-tree random forest predicting fuel efficiency (mpg) on the Auto MPG dataset (test RMSE 2.90, R² 0.854), served by Flask (`app.py`) with a Dockerfile. It needs scikit-learn 1.0.2 and Python ≤ 3.10 to load `model.pkl`. The internship certificate is in this folder.

```bash
cd legacy-auto-mpg
pip install -r requirements.txt
python app.py
```

It has been replaced by the Nepal used-car value estimator described in the [main README](../README.md).
