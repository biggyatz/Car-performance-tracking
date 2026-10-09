"""Export the trained random forest to web/model.json for the GitHub Pages app.

Each tree is stored as flat arrays: for node i, f[i] is the split feature
(-1 for a leaf), t[i] the threshold (or the leaf's prediction), and l[i]/r[i]
the child indexes. web/predict.js walks every tree and averages the leaves,
exactly like RandomForestRegressor.predict (including scikit-learn's float32
cast of the inputs before comparing against thresholds).

    python export_web_model.py
"""
import json
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)

trees = []
for estimator in model.estimators_:
    tree = estimator.tree_
    leaf = tree.children_left == -1
    trees.append({
        "f": [-1 if is_leaf else int(feat) for feat, is_leaf in zip(tree.feature, leaf)],
        "t": [float(v[0][0]) if is_leaf else float(thr)
              for thr, v, is_leaf in zip(tree.threshold, tree.value, leaf)],
        "l": tree.children_left.tolist(),
        "r": tree.children_right.tolist(),
    })

export = {"features": list(model.feature_names_in_), "trees": trees}
with open(os.path.join(BASE_DIR, "web", "model.json"), "w") as f:
    json.dump(export, f, separators=(",", ":"))
print(f"Wrote web/model.json ({len(trees)} trees)")
