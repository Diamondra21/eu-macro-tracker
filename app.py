import psycopg2
import pandas as pd
import plotly.express as px
import streamlit as st


def get_connection() -> psycopg2.extensions.connection:
    """Creates a PostgreSQL connection using Streamlit secrets."""
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require",
    )


st.set_page_config(
    page_title="EU Macro Tracker",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_worldbank_indicator(indicator_code: str) -> pd.DataFrame:
    """Loads annual WorldBank data for a given indicator across all countries."""
    conn = get_connection()
    query = """
        SELECT
            c.country_name,
            t.year,
            f.value
        FROM fact_indicators f
        JOIN dim_country   c ON c.country_id   = f.country_id
        JOIN dim_indicator i ON i.indicator_id = f.indicator_id
        JOIN dim_time      t ON t.time_id      = f.time_id
        WHERE i.indicator_code = %s
          AND t.period_type    = 'annual'
          AND f.value IS NOT NULL
        ORDER BY t.year, c.country_name
    """
    df = pd.read_sql(query, conn, params=(indicator_code,))
    conn.close()
    return df


@st.cache_data
def load_insee_monthly(series_code: str) -> pd.DataFrame:
    """Loads monthly INSEE data for a given series."""
    conn = get_connection()
    query = """
        SELECT
            t.year,
            t.month,
            f.value
        FROM fact_indicators f
        JOIN dim_indicator i ON i.indicator_id = f.indicator_id
        JOIN dim_time      t ON t.time_id      = f.time_id
        WHERE i.indicator_code = %s
          AND t.period_type    = 'monthly'
          AND f.value IS NOT NULL
        ORDER BY t.year, t.month
    """
    df = pd.read_sql(query, conn, params=(series_code,))
    conn.close()
    df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
    return df


st.title("📊 EU Macro Tracker")
st.markdown(
    "**How have inflation, unemployment and growth evolved in France "
    "compared to other European countries since the 2022 crisis?**"
)

inflation_df = load_worldbank_indicator("FP.CPI.TOTL.ZG")
peak = inflation_df.loc[inflation_df["value"].idxmax()]
st.info(
    f"🔍 **Key insight:** Peak inflation reached "
    f"**{peak['value']:.1f}%** in **{int(peak['year'])}** "
    f"(**{peak['country_name']}**) — highest level since 2000."
)

st.divider()

st.subheader("Inflation (annual %, WorldBank)")
fig_inf = px.line(
    inflation_df,
    x="year", y="value", color="country_name",
    labels={"year": "Year", "value": "Inflation (%)", "country_name": "Country"},
    markers=True,
)
fig_inf.update_layout(hovermode="x unified")
st.plotly_chart(fig_inf, use_container_width=True)

st.subheader("Unemployment rate (annual %, WorldBank)")
unemp_df = load_worldbank_indicator("SL.UEM.TOTL.ZS")
fig_unemp = px.line(
    unemp_df,
    x="year", y="value", color="country_name",
    labels={"year": "Year", "value": "Unemployment (%)", "country_name": "Country"},
    markers=True,
)
fig_unemp.update_layout(hovermode="x unified")
st.plotly_chart(fig_unemp, use_container_width=True)

st.subheader("GDP (current USD, WorldBank)")
gdp_df = load_worldbank_indicator("NY.GDP.MKTP.CD")
gdp_df["value_bn"] = gdp_df["value"] / 1e9
fig_gdp = px.line(
    gdp_df,
    x="year", y="value_bn", color="country_name",
    labels={"year": "Year", "value_bn": "GDP (billion USD)", "country_name": "Country"},
    markers=True,
)
fig_gdp.update_layout(hovermode="x unified")
st.plotly_chart(fig_gdp, use_container_width=True)

st.subheader("Consumer Price Index — France monthly (INSEE, Base 2015)")
ipc_df = load_insee_monthly("ipc_france")
fig_ipc = px.line(
    ipc_df,
    x="date", y="value",
    labels={"date": "Date", "value": "CPI Index"},
)
st.plotly_chart(fig_ipc, use_container_width=True)

st.caption("Sources: World Bank API · INSEE BDM API · Built with Python, PostgreSQL, Streamlit")