import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="India Airfare Price Index", page_icon="✈️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data_clean.csv", parse_dates=["snapshot_date"])
    return df

df = load_data()
st.title("✈️ India Airfare Price Index")
st.caption("SIH Problem Statement 56 — prototype using supplied Yatra airfare snapshots")


st.sidebar.header("Filters")
dates = sorted(df["snapshot_date"].dt.date.unique())
sel_dates = st.sidebar.multiselect("Snapshot dates", dates, default=dates)
airlines = sorted(df["airline"].unique())
sel_airlines = st.sidebar.multiselect("Airlines", airlines, default=airlines)
routes = sorted(df["route_code"].unique())
sel_routes = st.sidebar.multiselect("Routes", routes, default=routes)

f = df[df["snapshot_date"].dt.date.isin(sel_dates) &
       df["airline"].isin(sel_airlines) &
       df["route_code"].isin(sel_routes)].copy()

if f.empty:
    st.warning("No records match the selected filters.")
    st.stop()

route_day = (f.groupby(["snapshot_date","route_code"], as_index=False)
             .agg(fare=("price_inr","median"), observations=("price_inr","size")))
route_weights = {r: 1/len(sel_routes) for r in sel_routes}
route_day["weight"] = route_day["route_code"].map(route_weights)

base_date = min(route_day["snapshot_date"])
base = (route_day[route_day["snapshot_date"] == base_date]
        .set_index("route_code")["fare"].to_dict())

route_day["relative"] = route_day.apply(
    lambda x: (x["fare"] / base.get(x["route_code"], np.nan)) * 100, axis=1
)

index = (route_day.dropna(subset=["relative"])
         .groupby("snapshot_date")
         .apply(lambda g: np.average(g["relative"], weights=g["weight"]))
         .rename("index").reset_index())

latest = index.iloc[-1]["index"]
first = index.iloc[0]["index"]
change = latest - first
pct = (latest / first - 1) * 100 if first else np.nan

c1,c2,c3,c4 = st.columns(4)
c1.metric("Current Index", f"{latest:.2f}")
c2.metric("Base Index", "100.00")
c3.metric("Change vs base", f"{change:+.2f}")
c4.metric("Fare change", f"{pct:+.2f}%")

st.subheader("Airfare Price Index")
chart = index.set_index("snapshot_date")
st.line_chart(chart["index"])

st.subheader("🎬 3D Animated Airfare Price Analysis")

anim_df = (
    f.groupby(
        ["snapshot_date", "route_code", "airline"],
        as_index=False
    )
    .agg(
        fare=("price_inr", "median"),
        flights=("price_inr", "size")
    )
)


anim_df["snapshot"] = anim_df["snapshot_date"].dt.strftime("%d %b %Y")


fig_3d = px.scatter_3d(
    anim_df,
    x="route_code",
    y="airline",
    z="fare",
    color="route_code",
    size="flights",
    hover_data={
        "route_code": True,
        "airline": True,
        "fare": ":,.0f",
        "flights": True,
        "snapshot_date": True
    },
    animation_frame="snapshot",
    animation_group="route_code",
    title="3D Animated Airfare Prices",
    labels={
        "route_code": "Route",
        "airline": "Airline",
        "fare": "Median Fare (₹)"
    },
    height=650
)

fig_3d.update_layout(
    scene=dict(
        xaxis_title="Route",
        yaxis_title="Airline",
        zaxis_title="Median Fare (₹)"
    ),
    margin=dict(l=0, r=0, b=0, t=60)
)

st.plotly_chart(fig_3d, use_container_width=True)

st.caption(
    "Use the ▶ button to animate airfare changes across snapshot dates. "
    "You can also rotate, zoom and hover over individual observations."
)

st.subheader("Route-level index")
pivot = route_day.pivot_table(index="snapshot_date", columns="route_code", values="relative")
st.line_chart(pivot)

st.subheader("Average / median fare by route")
summary = (f.groupby("route_code")["price_inr"]
           .agg(["count","mean","median","min","max"])
           .round(0).rename(columns={"count":"Flights","mean":"Mean","median":"Median","min":"Min","max":"Max"}))
st.dataframe(summary, use_container_width=True)

st.subheader("Airline comparison")
air = (f.groupby(["snapshot_date","airline"])["price_inr"].median()
       .reset_index().pivot(index="snapshot_date", columns="airline", values="price_inr"))
st.line_chart(air)

st.subheader("Data explorer")
st.dataframe(f.sort_values(["snapshot_date","route_code","price_inr"]),
             use_container_width=True, height=420)

st.download_button("Download filtered CSV", f.to_csv(index=False),
                   file_name="airfare_filtered.csv", mime="text/csv")

with st.expander("Methodology"):
    st.markdown("""
**Prototype index method**

1. Clean and standardize airfare observations.
2. Group observations by route and snapshot date.
3. Use the **median fare** for each route-day to reduce outlier effects.
4. Set the earliest selected snapshot as the **base period = 100**.
5. Calculate each route's relative price: `Route Index = (Current Median / Base Median) × 100`.
6. Combine route indices using equal route weights in this prototype.

For a production CPI-aligned index, replace equal weights with official passenger expenditure/traffic weights and define a statistically defensible basket, seasonal treatment, taxes/fees policy, missing-price imputation and revision policy.
""")
