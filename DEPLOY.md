# 🚀 Deploy Guide — Will My Flight Be Late?

## Files needed
```
your-repo/
├── app.py
├── model.pkl
└── requirements.txt
```

---

## Step 1 — GitHub

1. Buat akun di https://github.com (gratis)
2. Buat repository baru → klik **New** → nama repo bebas (e.g. `flight-delay-predictor`)
3. Upload 3 file: `app.py`, `model.pkl`, `requirements.txt`

---

## Step 2 — Streamlit Community Cloud

1. Buka https://streamlit.io/cloud
2. Sign in dengan akun GitHub kamu
3. Klik **New app**
4. Pilih repository yang baru dibuat
5. Branch: `main`
6. Main file path: `app.py`
7. Klik **Deploy!**

Tunggu 2–3 menit → app langsung live dan dapat URL publik seperti:
`https://your-name-flight-delay-predictor.streamlit.app`

---

## Step 3 — Test

Buka URL-nya, isi form, klik **Check my flight** → boarding pass muncul!

---

## Cara generate ulang model.pkl (opsional)

Kalau mau retrain modelnya dari dataset terbaru, jalankan di Google Colab:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
import pickle

df = pd.read_csv('flight_data_2024.csv')
df_clean = df[df['cancelled'] == 0].dropna().copy()

df_clean['dep_hour']      = df_clean['dep_time'].astype(int) // 100
df_clean['is_weekend']    = (df_clean['day_of_week'] >= 6).astype(int)
df_clean['is_peak_month'] = df_clean['month'].isin([1,7,11,12]).astype(int)
df_clean['dep_period']    = df_clean['dep_hour'].apply(
    lambda h: 0 if h < 12 else 1 if h < 17 else 2 if h < 21 else 3)
df_clean['is_delayed']    = ((df_clean['weather_delay'] > 0) |
                              (df_clean['late_aircraft_delay'] > 0)).astype(int)

features      = ['month','day_of_month','day_of_week','dep_hour','dep_period','distance','is_weekend','is_peak_month']
cols_to_scale = ['dep_hour','distance','day_of_month']

X = df_clean[features]
y = df_clean['is_delayed']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = X_train.copy()
X_test_s  = X_test.copy()
X_train_s[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])
X_test_s[cols_to_scale]  = scaler.transform(X_test[cols_to_scale])

model = DecisionTreeClassifier(max_depth=8, random_state=42)
model.fit(X_train_s, y_train)

with open('model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'scaler': scaler,
                 'features': features, 'cols_to_scale': cols_to_scale}, f)

print('model.pkl saved! Upload to GitHub.')
```

---

## Notes
- App akan "tidur" setelah tidak diakses beberapa saat — otomatis bangun lagi saat dibuka
- Gratis tanpa batas untuk public apps
- Bisa share URL ke siapa saja tanpa login
