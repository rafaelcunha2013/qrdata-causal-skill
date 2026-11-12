"""Which standard estimator lands within 3% of the key? Development questions only.

Usage: python estimator_check.py
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
KEY = json.loads((ROOT / "key" / "effect.json").read_text())
SPLIT = json.loads((ROOT / "key" / "effect_split.json").read_text())


def estimand(text):
    if "on the treated" in text or "(ATT)" in text:
        return "ATT"
    if "on the control" in text or "(ATC)" in text:
        return "ATC"
    return "ATE"


def estimates(df, t, y, xs, target):
    X = df[xs].astype(float)
    T = df[t].astype(int)
    Y = df[y].astype(float)
    out = {"diff_means": Y[T == 1].mean() - Y[T == 0].mean()}
    ols = sm.OLS(Y, sm.add_constant(pd.concat([T, X], axis=1))).fit()
    out["ols"] = ols.params[t]
    m0 = sm.OLS(Y[T == 0], sm.add_constant(X[T == 0])).fit()
    m1 = sm.OLS(Y[T == 1], sm.add_constant(X[T == 1])).fit()
    mu0 = m0.predict(sm.add_constant(X))
    mu1 = m1.predict(sm.add_constant(X))
    group = {"ATE": T >= 0, "ATT": T == 1, "ATC": T == 0}[target]
    out["t_learner"] = (mu1 - mu0)[group].mean()
    ps = sm.Logit(T, sm.add_constant(X)).fit(disp=0).predict(sm.add_constant(X))
    if target == "ATT":
        w0 = ps / (1 - ps)
        out["ipw"] = Y[T == 1].mean() - np.average(Y[T == 0], weights=w0[T == 0])
    elif target == "ATC":
        w1 = (1 - ps) / ps
        out["ipw"] = np.average(Y[T == 1], weights=w1[T == 1]) - Y[T == 0].mean()
    else:
        out["ipw"] = np.mean(T * Y / ps) - np.mean((1 - T) * Y / (1 - ps))
    return out


rows = []
for task, side in sorted(SPLIT.items()):
    if side != "dev":
        continue
    folder = ROOT / "tasks_effect" / task
    files = [f for f in folder.iterdir() if f.name.startswith(("ihdp", "jobs"))]
    if not files:
        continue
    df = pd.read_csv(files[0])
    if files[0].name.startswith("ihdp"):
        t, y, xs = "treatment", "y", [f"x{i}" for i in range(1, 26)]
    else:
        t, y, xs = "t", "y", [f"x{i}" for i in range(0, 17)]
    target = estimand((folder / "question.md").read_text())
    key = float(re.findall(r"-?\d+\.?\d*", KEY[task]["answer"])[0])
    for name, value in estimates(df, t, y, xs, target).items():
        rows.append({"task": task, "file": files[0].stem, "estimand": target, "key": key,
                     "method": name, "value": round(value, 3),
                     "within_3pct": abs(value - key) <= 0.03 * abs(key)})

table = pd.DataFrame(rows)
print(table.pivot_table(index=["task", "file", "estimand", "key"], columns="method",
                        values="value").to_string())
print()
print("hits within 3% per method (dev):")
print(table.groupby("method")["within_3pct"].agg(["sum", "count"]).to_string())
