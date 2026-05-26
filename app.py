import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import random

st.set_page_config(
    page_title="Will My Flight Be Late?",
    page_icon="✈️",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }
.stDeployButton { display: none; }
footer { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 700px !important; }
div[data-testid="stForm"] { border: none; padding: 0; }
div.stButton > button {
    background-color: #1A3A5C !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important; font-size: 15px !important;
    font-weight: 500 !important; width: 100% !important;
}
div.stButton > button:hover { background-color: #2E86AB !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'rb') as f:
        return pickle.load(f)

artifact      = load_model()
model         = artifact['model']
scaler        = artifact['scaler']
features      = artifact['features']
cols_to_scale = artifact['cols_to_scale']

AIRPORTS = {
    'ATL':'Atlanta','DFW':'Dallas/Fort Worth','DEN':'Denver',
    'ORD':"Chicago O'Hare",'LAX':'Los Angeles','JFK':'New York JFK',
    'LGA':'New York LaGuardia','MCO':'Orlando','LAS':'Las Vegas',
    'PHX':'Phoenix','CLT':'Charlotte','MIA':'Miami',
    'SEA':'Seattle','BOS':'Boston','MSP':'Minneapolis',
    'SFO':'San Francisco','EWR':'Newark','IAH':'Houston',
}
MONTHS       = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
MONTHS_SHORT = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
DAYS         = {1:'Monday',2:'Tuesday',3:'Wednesday',4:'Thursday',5:'Friday',6:'Saturday',7:'Sunday'}


def build_factors(month, dow, dep_hour, distance, origin):
    factors = []
    is_peak    = month in [1, 7, 11, 12]
    is_weekend = dow >= 6
    dep_period = 0 if dep_hour < 12 else 1 if dep_hour < 17 else 2 if dep_hour < 21 else 3
    high_risk  = ['ORD','LGA','JFK','BOS','DEN','EWR']

    if is_peak:
        factors.append(('risk', 'January — high winter storm risk' if month == 1 else 'Peak travel month — higher delay probability'))
    else:
        factors.append(('safe', 'Off-peak month — lower weather risk'))

    if dep_period == 2:
        factors.append(('risk', 'Evening departure — delays accumulate through the day'))
    elif dep_period == 3:
        factors.append(('risk', 'Late night departure — residual delay risk'))
    elif dep_period == 0:
        factors.append(('safe', 'Morning departure — fewest accumulated delays'))
    else:
        factors.append(('neutral', 'Afternoon departure — moderate risk'))

    factors.append(('risk', 'Weekend — higher passenger volume') if is_weekend
                   else ('safe', 'Weekday — typically lighter congestion'))

    if distance > 2000:
        factors.append(('neutral', f'Long-haul ({distance:,} mi) — more weather exposure'))
    elif distance < 500:
        factors.append(('safe', f'Short-haul ({distance:,} mi) — less weather exposure'))
    else:
        factors.append(('neutral', f'Medium-distance ({distance:,} mi)'))

    if origin in high_risk:
        factors.append(('risk', f'{origin} — high congestion or weather exposure'))

    return factors


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<p style="font-size:12px;font-weight:500;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">
Future Classroom · Machine Learning</p>
<p style="font-size:26px;font-weight:600;color:#111827;margin-bottom:0;">✈️ Will my flight be late?</p>
<span style="background:#eff6ff;color:#1e40af;font-size:11px;padding:4px 10px;border-radius:6px;font-weight:500;">
Powered by Decision Tree · Trained on 1M+ flights · 89% accuracy</span>
<br><br>
""", unsafe_allow_html=True)

# ── Form ─────────────────────────────────────────────────────────────────────
with st.form("flight_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin    = st.selectbox('Origin airport', list(AIRPORTS.keys()),
                      format_func=lambda x: f"{x} — {AIRPORTS[x]}",
                      index=list(AIRPORTS.keys()).index('JFK'))
        month     = st.selectbox('Month', list(MONTHS.keys()),
                      format_func=lambda x: MONTHS[x], index=0)
        dep_hour  = st.selectbox('Departure time', list(range(5,23)),
                      format_func=lambda x: f"{x:02d}:00 {'AM' if x<12 else 'PM'}", index=4)
    with col2:
        dest      = st.selectbox('Destination airport', list(AIRPORTS.keys()),
                      format_func=lambda x: f"{x} — {AIRPORTS[x]}",
                      index=list(AIRPORTS.keys()).index('LAX'))
        dow       = st.selectbox('Day of week', list(DAYS.keys()),
                      format_func=lambda x: DAYS[x], index=2)
        distance  = st.number_input('Distance (miles)', min_value=50, max_value=5000, value=2475, step=50)

    day_of_month = st.slider('Day of month', min_value=1, max_value=28, value=15)
    submitted    = st.form_submit_button("✈️  Check my flight")

# ── Result ───────────────────────────────────────────────────────────────────
if submitted:
    is_weekend    = 1 if dow >= 6 else 0
    is_peak_month = 1 if month in [1,7,11,12] else 0
    dep_period    = 0 if dep_hour < 12 else 1 if dep_hour < 17 else 2 if dep_hour < 21 else 3

    input_df = pd.DataFrame([{
        'month': month, 'day_of_month': day_of_month, 'day_of_week': dow,
        'dep_hour': dep_hour, 'dep_period': dep_period, 'distance': distance,
        'is_weekend': is_weekend, 'is_peak_month': is_peak_month,
    }])
    input_scaled = input_df.copy()
    input_scaled[cols_to_scale] = scaler.transform(input_df[cols_to_scale])

    prediction  = model.predict(input_scaled[features])[0]
    proba       = model.predict_proba(input_scaled[features])[0]
    delay_prob  = round(proba[1] * 100)
    ontime_prob = round(proba[0] * 100)
    confidence  = delay_prob if prediction == 1 else ontime_prob
    is_delayed  = prediction == 1

    factors = build_factors(month, dow, dep_hour, distance, origin)
    random.seed(month + dow + dep_hour)
    seat      = random.choice(['12A','14B','16C','22D','8F','27A','31C','5B','19D','11E'])
    gate      = random.choice(['A12','A18','B04','B22','C11','C33','D07','D15','E02','E19'])
    flight_no = f"FL {random.randint(1000,9999)}"

    verdict_txt   = '⚠️  Likely Delayed' if is_delayed else '✅  On Time'
    verdict_color = '#991b1b' if is_delayed else '#166534'
    bar_color     = '#dc2626' if is_delayed else '#16a34a'
    conf_color    = '#991b1b' if is_delayed else '#166534'

    factor_colors = {'risk':'#dc2626','safe':'#16a34a','neutral':'#9ca3af'}
    factors_html  = ''.join(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;font-size:13px;color:#4b5563;">'
        f'<span style="color:{factor_colors[t]};font-size:10px;">●</span>'
        f'<span>{txt}</span></div>'
        for t, txt in factors
    )

    bar_width = confidence

    html = f"""
<div style="background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;margin-top:1rem;">

  <div style="background:#1A3A5C;padding:18px 24px;display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:3px;">Boarding pass</div>
      <div style="font-size:18px;font-weight:600;color:#ffffff;letter-spacing:0.04em;">Future Airlines</div>
    </div>
    <div style="font-size:13px;color:rgba(255,255,255,0.8);font-family:monospace;">{flight_no}</div>
  </div>

  <div style="padding:20px 24px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px dashed #e5e7eb;">
    <div>
      <div style="font-size:40px;font-weight:700;color:#111827;line-height:1;font-family:monospace;">{origin}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">{AIRPORTS.get(origin,origin)}</div>
    </div>
    <div style="font-size:28px;color:#d1d5db;">✈</div>
    <div style="text-align:right;">
      <div style="font-size:40px;font-weight:700;color:#111827;line-height:1;font-family:monospace;">{dest}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">{AIRPORTS.get(dest,dest)}</div>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(4,1fr);padding:14px 24px;gap:8px;border-bottom:1px dashed #e5e7eb;">
    <div>
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;">Month</div>
      <div style="font-size:14px;font-weight:600;color:#111827;margin-top:3px;font-family:monospace;">{MONTHS_SHORT[month]}</div>
    </div>
    <div>
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;">Departs</div>
      <div style="font-size:14px;font-weight:600;color:#111827;margin-top:3px;font-family:monospace;">{dep_hour:02d}:00</div>
    </div>
    <div>
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;">Distance</div>
      <div style="font-size:14px;font-weight:600;color:#111827;margin-top:3px;font-family:monospace;">{distance:,} mi</div>
    </div>
    <div>
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;">Day</div>
      <div style="font-size:14px;font-weight:600;color:#111827;margin-top:3px;font-family:monospace;">{DAYS[dow][:3]}</div>
    </div>
  </div>

  <div style="padding:20px 24px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:5px;">ML Prediction</div>
      <div style="font-size:26px;font-weight:700;color:{verdict_color};">{verdict_txt}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;">Confidence</div>
      <div style="background:#f3f4f6;border-radius:4px;height:6px;width:130px;overflow:hidden;">
        <div style="background:{bar_color};height:100%;border-radius:4px;width:{bar_width}%;"></div>
      </div>
      <div style="font-size:14px;font-weight:600;color:{conf_color};margin-top:5px;">{confidence}%</div>
    </div>
  </div>

  <div style="padding:0 24px 20px;border-top:1px solid #f3f4f6;padding-top:14px;">
    <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">Risk factors</div>
    {factors_html}
  </div>

  <div style="border-top:1px dashed #d1d5db;padding:12px 24px;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:11px;color:#9ca3af;font-family:monospace;">Seat {seat} &nbsp;|&nbsp; Gate {gate}</div>
    <div style="font-size:11px;color:#9ca3af;font-family:monospace;">||| || ||| | || ||| || | ||</div>
  </div>

</div>

<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 18px;font-size:13px;color:#166534;margin-top:1rem;">
  <strong>How this works:</strong> This uses a real Decision Tree trained on 1,022,824 US domestic flights (2024).
  Features: month, day of week, departure hour, departure period, distance, is_weekend, is_peak_month.
  Trained in Lesson 3 using scikit-learn. Test accuracy: <strong>89%</strong>.
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
