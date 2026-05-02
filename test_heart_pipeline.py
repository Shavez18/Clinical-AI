"""Quick verification test for the fixed heart prediction pipeline."""
import sys
sys.path.insert(0, r"C:\Major project\ai-health-assistant")

from src.predict_heart import predict_heart

results = []

# ── Test 1: High-risk profile ─────────────────────────────────────────────────
p1, pred1 = predict_heart(
    age=65, sex=1, cp=3, trestbps=160, chol=250,
    fbs=1, restecg=1, thalach=90, exang=1,
    oldpeak=3.5, slope=0, ca=3, thal=2,
)
ok1 = p1 > 0.60
results.append(("HIGH-RISK", p1, pred1, ok1, "> 60%"))

# ── Test 2: Low-risk profile ──────────────────────────────────────────────────
p2, pred2 = predict_heart(
    age=30, sex=0, cp=0, trestbps=110, chol=170,
    fbs=0, restecg=0, thalach=175, exang=0,
    oldpeak=0.0, slope=2, ca=0, thal=0,
)
ok2 = p2 < 0.40
results.append(("LOW-RISK", p2, pred2, ok2, "< 40%"))

# ── Test 3: Validation — zero BP should raise ValueError ─────────────────────
try:
    predict_heart(
        age=45, sex=1, cp=0, trestbps=0, chol=200,
        fbs=0, restecg=0, thalach=150, exang=0,
        oldpeak=1.0, slope=1, ca=0, thal=0,
    )
    ok3 = False
    val_msg = "FAIL — should have raised ValueError"
except ValueError as e:
    ok3 = True
    val_msg = f"OK — {e}"
results.append(("VALIDATION (0 BP)", None, None, ok3, "ValueError raised"))

# ── Print results ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("HEART PIPELINE VERIFICATION")
print("=" * 60)
for label, prob, pred, ok, expected in results:
    status = "PASS" if ok else "FAIL"
    if prob is not None:
        print(f"[{status}] {label:20s} P(disease)={prob*100:.1f}%  expected {expected}  pred={'High' if pred==1 else 'Low'}")
    else:
        print(f"[{status}] {label:20s} {val_msg}")

all_ok = all(r[3] for r in results)
print("=" * 60)
print("ALL TESTS PASSED" if all_ok else "SOME TESTS FAILED")
print("=" * 60)
sys.exit(0 if all_ok else 1)
