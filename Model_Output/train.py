"""Churn prediction model for the SaiKet Power BI internship (own work).
5-fold stratified cross-validated logistic regression: every customer gets an out-of-fold score."""
import sys, json
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

src, outdir = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, dtype=str)
for c in ["SeniorCitizen", "tenure"]: df[c] = df[c].astype(int)
df["MonthlyCharges"] = df.MonthlyCharges.astype(float)
df["TotalCharges"] = pd.to_numeric(df.TotalCharges.str.strip().replace("", np.nan)).fillna(0.0)
y = (df.Churn == "Yes").astype(int)
num = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
cat = [c for c in df.columns if c not in num + ["customerID", "Churn"]]
pre = ColumnTransformer([("n", StandardScaler(), num), ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
pipe = Pipeline([("p", pre), ("m", LogisticRegression(max_iter=2000, C=0.5))])
cv = StratifiedKFold(5, shuffle=True, random_state=2026)
prob = cross_val_predict(pipe, df.drop(columns=["customerID", "Churn"]), y, cv=cv, method="predict_proba")[:, 1]
pred = (prob >= 0.5).astype(int)
tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
metrics = {"customers": int(len(df)), "roc_auc": roc_auc_score(y, prob), "accuracy": accuracy_score(y, pred),
           "precision": precision_score(y, pred), "recall": recall_score(y, pred), "f1": f1_score(y, pred),
           "baseline_accuracy": 1 - y.mean(), "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
print(json.dumps(metrics, indent=1))

risk = pd.cut(prob, [-1, 0.2, 0.5, 2], labels=["Low", "Medium", "High"], right=False)
scores = pd.DataFrame({"customerID": df.customerID, "Churn Probability": prob.round(4), "Risk Level": risk.astype(str),
                       "Actual": np.where(y == 1, "Churned", "Retained"), "Predicted": np.where(pred == 1, "Churn", "Stay")})
scores.to_csv(f"{outdir}/Customer_Risk_Scores.csv", index=False)
print(scores["Risk Level"].value_counts().to_dict())

# drivers: coefficients of the final model fitted on all customers
pipe.fit(df.drop(columns=["customerID", "Churn"]), y)
names = pipe.named_steps["p"].get_feature_names_out()
coef = pipe.named_steps["m"].coef_[0]
def nice(n):
    n = n.split("__", 1)[1]
    return {"tenure": "Tenure (months)", "MonthlyCharges": "Monthly charges", "TotalCharges": "Total charges", "SeniorCitizen": "Senior citizen"}.get(n, n.replace("_", " = ", 1))
drv = pd.DataFrame({"Feature": [nice(n) for n in names], "Effect": coef})
drv = drv[~drv.Feature.str.endswith(("= No", "= No internet service", "= No phone service"))]  # keep the informative level of each pair
drv = drv.reindex(drv.Effect.abs().sort_values(ascending=False).index).head(12)
drv["Effect"] = drv.Effect.round(3)
drv["Direction"] = np.where(drv.Effect > 0, "Raises churn risk", "Lowers churn risk")
drv.to_csv(f"{outdir}/Model_Drivers.csv", index=False)
print(drv.to_string(index=False))

# retention list: observed-retained customers the model flags as high risk
raw = df[["customerID", "Contract", "InternetService", "PaymentMethod", "tenure", "MonthlyCharges"]].merge(scores, on="customerID")
lst = raw[(raw.Actual == "Retained") & (raw["Risk Level"] == "High")].sort_values("Churn Probability", ascending=False)
lst = lst[["customerID", "Contract", "InternetService", "PaymentMethod", "tenure", "MonthlyCharges", "Churn Probability", "Risk Level"]].rename(columns={"tenure": "Tenure"})
lst.to_csv(f"{outdir}/Retention_Priority_List.csv", index=False)
print("retention list rows:", len(lst))
json.dump(metrics, open(f"{outdir}/Model_Metrics.json", "w"), indent=1)
