import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

st.set_page_config(
    page_title="Will My Flight Be Late?",
    page_icon="✈️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background-color: #f8f9fa; }
.block-container { padding: 2rem 1.5rem; max-width: 680px; }

.page-title {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 24px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0;
}

.boarding-pass {
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
    margin-top: 1.5rem;
}
.bp-header {
    background: #1A3A5C;
    padding: 18px 24px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.bp-airline {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: 0.04em;
}
.bp-header-sub {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
}
.bp-flight-no {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: rgba(255,255,255,0.8);
}
.bp-route {
    padding: 20px 24px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px dashed #e5e7eb;
}
.bp-code {
    font-size: 40px;
    font-weight: 600;
    color: #111827;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.bp-city { font-size: 12px; color: #6b7280; margin-top: 4px; }
.bp-arrow { font-size: 24px; color: #d1d5db; }
.bp-details {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    padding: 14px 24px;
    gap: 8px;
    border-bottom: 1px dashed #e5e7eb;
}
.bp-detail-label {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.bp-detail-value {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
    margin-top: 3px;
    font-family: 'JetBrains Mono', monospace;
}
.bp-result {
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.bp-verdict-label {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 5px;
}
.bp-verdict-ontime {
    font-size: 26px;
    font-weight: 600;
    color: #166534;
}
.bp-verdict-delayed {
    font-size: 26px;
    font-weight: 600;
    color: #991b1b;
}
.bp-conf-label {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 6px;
    text-align: right;
}
.bp-conf-pct-ontime {
    font-size: 14px;
    font-weight: 600;
    color: #166534;
    text-align: right;
    margin-top: 5px;
}
.bp-conf-pct-delayed {
    font-size: 14px;
    font-weight: 600;
    color: #991b1b;
    text-align: right;
    margin-top: 5px;
}
.bp-factors {
    padding: 14px 24px 20px;
    border-top: 1px solid #f3f4f6;
}
.bp-factors-title {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 10px;
}
.factor-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 7px;
    font-size: 13px;
    color: #4b5563;
}
.dot-risk { color: #dc2626; }
.dot-safe { color: #16a34a; }
.dot-neutral { color: #9ca3af; }
.bp-stub {
    border-top: 1px dashed #d1d5db;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.bp-stub-text {
    font-size: 11px;
    color: #9ca3af;
    font-family: 'JetBrains Mono', monospace;
}
.progress-bar-bg {
    background: #f3f4f6;
    border-radius: 4px;
    height: 6px;
    width: 130px;
    overflow: hidden;
}
.progress-bar-ontime {
    background: #16a34a;
    height: 100%;
    border-radius: 4px;
}
.progress-bar-delayed {
    background: #dc2626;
    height: 100%;
    border-radius: 4px;
}
.ml-badge {
    background: #eff6ff;
    color: #1e40af;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 1rem;
    font-weight: 500;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

div.stButton > button {
    background-color: #1A3A5C;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 15px;
    font-weight: 500;
    width: 100%;
    letter-spacing: 0.02em;
}
div.stButton > button:hover { background-color: #2E86AB; border: none; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'rb') as f:
        return pickle.load(f)

artifact = load_model()
model    = artifact['model']
scaler   = artifact['scaler']
features = artifact['features']
cols_to_scale = artifact['cols_to_scale']

AIRPORTS = {
    'ATL': 'Atlanta', 'DFW': 'Dallas/Fort Worth', 'DEN': 'Denver',
    'ORD': "Chicago O'Hare", 'LAX': 'Los Angeles', 'JFK': 'New York JFK',
    'LGA': 'New York LaGuardia', 'MCO': 'Orlando', 'LAS': 'Las Vegas',
    'PHX': 'Phoenix', 'CLT': 'Charlotte', 'MIA': 'Miami',
    'SEA': 'Seattle', 'BOS': 'Boston', 'MSP': 'Minneapolis',
    'SFO': 'San Francisco', 'EWR': 'Newark', 'IAH': 'Houston Intercontinental',
}

MONTHS = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
          7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
MONTHS_SHORT = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
DAYS = {1:'Monday',2:'Tuesday',3:'Wednesday',4:'Thursday',5:'Friday',6:'Saturday',7:'Sunday'}


def build_factors(month, dow, dep_hour, distance, origin):
    factors = []
    is_peak = month in [1, 7, 11, 12]
    is_weekend = dow >= 6
    dep_period = 0 if dep_hour < 12 else 1 if dep_hour < 17 else 2 if dep_hour < 21 else 3
    high_risk_origins = ['ORD', 'LGA', 'JFK', 'BOS', 'DEN', 'EWR']

    if is_peak:
        label = 'January — high winter storm risk' if month == 1 else 'Peak travel month — higher delay probability'
        factors.append(('risk', label))
    else:
        factors.append(('safe', 'Off-peak month — lower weather risk'))

    if dep_period == 2:
        factors.append(('risk', 'Evening departure — delays accumulate through the day'))
    elif dep_period == 3:
        factors.append(('risk', 'Late night departure — some residual delay risk'))
    elif dep_period == 0:
        factors.append(('safe', 'Morning departure — fewest accumulated delays'))
    else:
        factors.append(('neutral', 'Afternoon departure — moderate risk'))

    if is_weekend:
        factors.append(('risk', 'Weekend — higher passenger volume'))
    else:
        factors.append(('safe', 'Weekday — typically lighter congestion'))

    if distance > 2000:
        factors.append(('neutral', f'Long-haul flight ({distance:,} mi) — more weather exposure'))
    elif distance < 500:
        factors.append(('safe', f'Short-haul flight ({distance:,} mi) — less weather exposure'))
    else:
        factors.append(('neutral', f'Medium-distance flight ({distance:,} mi)'))

    if origin in high_risk_origins:
        factors.append(('risk', f'{origin} — airport with high congestion or weather exposure'))

    return factors


st.markdown('<p class="page-title">Future Classroom · Machine Learning</p>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">✈️ Will my flight be late?</p>', unsafe_allow_html=True)
st.markdown('<span class="ml-badge">Powered by Decision Tree · Trained on 1M+ flights · 89% accuracy</span>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

with st.form("flight_form"):
    col1, col2 = st.columns(2)

    with col1:
        origin = st.selectbox('Origin airport',
            options=list(AIRPORTS.keys()),
            format_func=lambda x: f"{x} — {AIRPORTS[x]}",
            index=list(AIRPORTS.keys()).index('JFK'))

        month = st.selectbox('Month',
            options=list(MONTHS.keys()),
            format_func=lambda x: MONTHS[x],
            index=0)

        dep_hour = st.selectbox('Departure time',
            options=list(range(5, 23)),
            format_func=lambda x: f"{x:02d}:00 {'AM' if x < 12 else 'PM'}",
            index=4)

    with col2:
        dest = st.selectbox('Destination airport',
            options=list(AIRPORTS.keys()),
            format_func=lambda x: f"{x} — {AIRPORTS[x]}",
            index=list(AIRPORTS.keys()).index('LAX'))

        dow = st.selectbox('Day of week',
            options=list(DAYS.keys()),
            format_func=lambda x: DAYS[x],
            index=2)

        distance = st.number_input('Distance (miles)', min_value=50, max_value=5000, value=2475, step=50)

    day_of_month = st.slider('Day of month', min_value=1, max_value=28, value=15)

    submitted = st.form_submit_button("✈️  Check my flight")

if submitted:
    is_weekend   = 1 if dow >= 6 else 0
    is_peak_month = 1 if month in [1, 7, 11, 12] else 0
    dep_period   = 0 if dep_hour < 12 else 1 if dep_hour < 17 else 2 if dep_hour < 21 else 3

    input_df = pd.DataFrame([{
        'month': month,
        'day_of_month': day_of_month,
        'day_of_week': dow,
        'dep_hour': dep_hour,
        'dep_period': dep_period,
        'distance': distance,
        'is_weekend': is_weekend,
        'is_peak_month': is_peak_month,
    }])

    input_scaled = input_df.copy()
    input_scaled[cols_to_scale] = scaler.transform(input_df[cols_to_scale])

    prediction   = model.predict(input_scaled[features])[0]
    proba        = model.predict_proba(input_scaled[features])[0]
    delay_prob   = round(proba[1] * 100)
    ontime_prob  = round(proba[0] * 100)
    confidence   = delay_prob if prediction == 1 else ontime_prob

    is_delayed  = prediction == 1
    verdict_cls = 'bp-verdict-delayed' if is_delayed else 'bp-verdict-ontime'
    verdict_txt = '⚠️  Likely Delayed' if is_delayed else '✅  On Time'
    bar_cls     = 'progress-bar-delayed' if is_delayed else 'progress-bar-ontime'
    conf_cls    = 'bp-conf-pct-delayed' if is_delayed else 'bp-conf-pct-ontime'

    factors    = build_factors(month, dow, dep_hour, distance, origin)
    import random; random.seed(month + dow + dep_hour)
    seat       = random.choice(['12A','14B','16C','22D','8F','27A','31C','5B','19D','11E'])
    gate       = random.choice(['A12','A18','B04','B22','C11','C33','D07','D15','E02','E19'])
    flight_no  = f"FL {random.randint(1000,9999)}"

    factors_html = ''
    dot_map = {'risk': '●', 'safe': '●', 'neutral': '●'}
    color_map = {'risk': '#dc2626', 'safe': '#16a34a', 'neutral': '#9ca3af'}
    for ftype, ftxt in factors:
        factors_html += f'''
        <div class="factor-row">
            <span style="color:{color_map[ftype]};font-size:10px;">●</span>
            <span>{ftxt}</span>
        </div>'''

    st.markdown(f"""
    <div class="boarding-pass">
        <div class="bp-header">
            <div>
                <div class="bp-header-sub">Boarding pass</div>
                <div class="bp-airline">Future Airlines</div>
            </div>
            <div class="bp-flight-no">{flight_no}</div>
        </div>

        <div class="bp-route">
            <div>
                <div class="bp-code">{origin}</div>
                <div class="bp-city">{AIRPORTS.get(origin, origin)}</div>
            </div>
            <div class="bp-arrow">✈</div>
            <div style="text-align:right;">
                <div class="bp-code">{dest}</div>
                <div class="bp-city">{AIRPORTS.get(dest, dest)}</div>
            </div>
        </div>

        <div class="bp-details">
            <div>
                <div class="bp-detail-label">Month</div>
                <div class="bp-detail-value">{MONTHS_SHORT[month]}</div>
            </div>
            <div>
                <div class="bp-detail-label">Departs</div>
                <div class="bp-detail-value">{dep_hour:02d}:00</div>
            </div>
            <div>
                <div class="bp-detail-label">Distance</div>
                <div class="bp-detail-value">{distance:,} mi</div>
            </div>
            <div>
                <div class="bp-detail-label">Day</div>
                <div class="bp-detail-value">{DAYS[dow][:3]}</div>
            </div>
        </div>

        <div class="bp-result">
            <div>
                <div class="bp-verdict-label">ML Prediction</div>
                <div class="{verdict_cls}">{verdict_txt}</div>
            </div>
            <div>
                <div class="bp-conf-label">Confidence</div>
                <div class="progress-bar-bg">
                    <div class="{bar_cls}" style="width:{confidence}%;"></div>
                </div>
                <div class="{conf_cls}">{confidence}%</div>
            </div>
        </div>

        <div class="bp-factors">
            <div class="bp-factors-title">Risk factors</div>
            {factors_html}
        </div>

        <div class="bp-stub">
            <div class="bp-stub-text">Seat {seat} &nbsp;|&nbsp; Gate {gate}</div>
            <div class="bp-stub-text">🟥🟦🟥🟦🟥🟦🟥🟦🟥🟦</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <br>
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 18px;font-size:13px;color:#166534;">
        <strong>How this works:</strong> This prediction uses a real Decision Tree model trained on {1022824:,} US domestic flights from 2024.
        The model was trained in Lesson 3 using scikit-learn with features: month, day of week, departure hour, departure period,
        distance, is_weekend, and is_peak_month. Test accuracy: <strong>89%</strong>.
    </div>
    """, unsafe_allow_html=True)
