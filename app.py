import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go

from data.fred import (
    get_core_pce,
    get_cpi,
    get_unemployment,
    get_gdp,
    get_fed_rate,
    get_m2
)

from data.market import get_sp500, get_btc
from signals.transforms import yoy_change, qoq_annualized

# =========================================
# PAGE
# =========================================
st.set_page_config(layout="wide")
st.title("Macro Engine 🚀")

# =========================================
# SIDEBAR
# =========================================
years = st.sidebar.slider("Years Back", 1, 20, 5)

st.sidebar.markdown("---")
st.sidebar.subheader("Select Indicators")

selected = []

with st.sidebar.expander("Sensors", True):
    if st.checkbox("Core PCE (YoY %)", True):
        selected.append("Core PCE")
    if st.checkbox("CPI (YoY %)", True):
        selected.append("CPI")
    if st.checkbox("Unemployment Rate", True):
        selected.append("Unemployment")
    if st.checkbox("GDP (QoQ annualized)", True):
        selected.append("GDP")

with st.sidebar.expander("Policy", True):
    if st.checkbox("Fed Rate", True):
        selected.append("Fed Rate")
    if st.checkbox("M2", False):
        selected.append("M2")

with st.sidebar.expander("Market", True):
    if st.checkbox("S&P500", True):
        selected.append("S&P500")
    if st.checkbox("BTC", False):
        selected.append("BTC")

# =========================================
# TIME
# =========================================
end = datetime.datetime.now()
start = end - datetime.timedelta(days=years * 365)

# =========================================
# KPI DATA (ALWAYS LOADED)
# =========================================
kpi_data = {}

kpi_data["Core PCE (YoY %)"] = get_core_pce(start, end).apply(yoy_change)
kpi_data["CPI (YoY %)"] = get_cpi(start, end).apply(yoy_change)
kpi_data["Unemployment (%)"] = get_unemployment(start, end)
kpi_data["GDP (QoQ ann %)"] = qoq_annualized(get_gdp(start, end)["GDP"]).to_frame("GDP (QoQ ann %)")
kpi_data["Fed Rate (%)"] = get_fed_rate(start, end)

# =========================================
# DATA FETCH (BASED ON SELECTION)
# =========================================
data_dict = {}

if "Core PCE" in selected:
    data_dict["Core PCE"] = get_core_pce(start, end).apply(yoy_change)

if "CPI" in selected:
    data_dict["CPI"] = get_cpi(start, end).apply(yoy_change)

if "Unemployment" in selected:
    data_dict["Unemployment"] = get_unemployment(start, end)

if "GDP" in selected:
    data_dict["GDP"] = qoq_annualized(get_gdp(start, end)["GDP"]).to_frame("GDP")

if "Fed Rate" in selected:
    data_dict["Fed Rate"] = get_fed_rate(start, end)

if "M2" in selected:
    data_dict["M2"] = get_m2(start, end)

if "S&P500" in selected:
    data_dict["S&P500"] = get_sp500(start, end)

if "BTC" in selected:
    data_dict["BTC"] = get_btc(start, end)

# =========================================
# KPI ROW
# =========================================
st.subheader("Macro Snapshot")

cols = st.columns(5)

def get_color(value, name):

    # -------- Inflation --------
    if name in ["Core PCE", "CPI"]:
        if value <= 2.2:
            return "green"
        elif value <= 3.0:
            return "orange"
        else:
            return "red"

    # -------- Unemployment --------
    elif name == "Unemployment":
        if value <= 4:
            return "green"
        elif value <= 5:
            return "orange"
        else:
            return "red"

    # -------- GDP --------
    elif name == "GDP":
        if value > 2:
            return "green"
        elif value > 0:
            return "orange"
        else:
            return "red"

    # -------- Fed Rate --------
    elif name == "Fed Rate":
        if value < 2:
            return "green"
        elif value <= 3:
            return "orange"
        else:
            return "red"

    return "white"


def show_kpi(col, title, df, name):
    value = df.iloc[-1, 0]
    date = df.index[-1].date()
    color = get_color(value, name)

    col.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:14px; color:gray;">{title}</div>
            <div style="font-size:28px; color:{color}; font-weight:bold;">
                {value:.2f}
            </div>
            <div style="font-size:12px; color:gray;">
                As of {date}
            </div>
        </div>
    """, unsafe_allow_html=True)


show_kpi(cols[0], "Core PCE (YoY %)", kpi_data["Core PCE (YoY %)"], "Core PCE")
show_kpi(cols[1], "CPI (YoY %)", kpi_data["CPI (YoY %)"], "CPI")
show_kpi(cols[2], "Unemployment (%)", kpi_data["Unemployment (%)"], "Unemployment")
show_kpi(cols[3], "GDP (QoQ ann %)", kpi_data["GDP (QoQ ann %)"], "GDP")
show_kpi(cols[4], "Fed Rate (%)", kpi_data["Fed Rate (%)"], "Fed Rate")

# =========================================
# OVERLAY
# =========================================
st.subheader("Overlay View")

if not data_dict:
    st.warning("Select indicators from sidebar")
    st.stop()

overlay_df = pd.concat(data_dict.values(), axis=1).ffill()

fig = go.Figure()

for col in overlay_df.columns:
    fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df[col], mode="lines", name=col))

fig.update_layout(template="plotly_dark", height=500, legend=dict(orientation="h", y=-0.2))

st.plotly_chart(fig, use_container_width=True)

# =========================================
# INDIVIDUAL VIEWS
# =========================================
st.subheader("Individual Views")

items = list(data_dict.items())

for i in range(0, len(items), 2):
    cols = st.columns(2)

    for j in range(2):
        if i + j < len(items):
            name, df = items[i + j]

            with cols[j]:
                st.write(f"### {name}")

                chart_type = st.radio(f"{name} view", ["Line", "Bar"], horizontal=True, key=name)

                df_clean = df.copy()
                df_clean.columns = [name]

                if chart_type == "Line":
                    st.line_chart(df_clean, use_container_width=True)
                else:
                    st.bar_chart(df_clean, use_container_width=True)

                with st.expander("Show raw data"):
                    df_display = df_clean.copy()
                    df_display.index = df_display.index.date
                    st.dataframe(df_display.sort_index(ascending=False).head(20))