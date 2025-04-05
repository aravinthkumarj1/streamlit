import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache
# Changed from @st.cache_data to @st.cache for compatibility

def load_data():
    df = pd.read_excel("NSE_Indian_Stock_Data_5_4.xlsx", sheet_name="NSE_2025")
    df = df.dropna(subset=[col for col in df.columns if "_Diff" in col])
    return df

df = load_data()

st.title("📊 Indian Stock Market Dashboard")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    sectors = df['sector'].dropna().unique()
    selected_sector = st.multiselect("Select Sector(s)", sectors)

    industries = df['industry'].dropna().unique()
    selected_industry = st.multiselect("Select Industry(s)", industries)

    volatile_only = st.checkbox("Show only volatile stocks (>5% daily movement)")
    min_2025_growth = st.slider("Minimum 2025 Growth %", min_value=0, max_value=int(df['2025'].max()), value=0)

# Apply filters
filtered_df = df.copy()

if selected_sector:
    filtered_df = filtered_df[filtered_df['sector'].isin(selected_sector)]

if selected_industry:
    filtered_df = filtered_df[filtered_df['industry'].isin(selected_industry)]

if volatile_only:
    filtered_df = filtered_df[filtered_df['Stock_Volatile_Percentage'] > 5]

filtered_df = filtered_df[filtered_df['2025'] >= min_2025_growth]

# Show summary
st.subheader("📈 Top Stocks by 2025 Growth")
st.dataframe(filtered_df[['Symbol_Input', 'shortName', 'sector', 'industry', '2025', 'Stock_Volatile_Percentage']].sort_values(by='2025', ascending=False).reset_index(drop=True))

# Stock selector for visualization
if not filtered_df.empty:
    selected_stock = st.selectbox("Select a stock to visualize", filtered_df['Symbol_Input'].unique())
    stock_data = df[df['Symbol_Input'] == selected_stock].iloc[0]

    # Extract daily difference columns
    daily_cols = [col for col in df.columns if col.startswith("D") and col.endswith("_Diff")]
    daily_series = stock_data[daily_cols].dropna()

    try:
        daily_series.index = pd.to_datetime([col.replace("_Diff", "") for col in daily_series.index])

        # Plot daily price change
        fig = px.line(x=daily_series.index, y=daily_series.values, labels={'x': 'Date', 'y': 'Daily Change'}, title=f"Daily Price Movement - {selected_stock}")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not plot daily data: {e}")

    # Add overall stats
    st.markdown("---")
    st.markdown(f"**Short Name:** {stock_data['shortName']}  ")
    st.markdown(f"**Sector:** {stock_data['sector']}  ")
    st.markdown(f"**Industry:** {stock_data['industry']}  ")
    st.markdown(f"**2025 Total Growth:** {stock_data['2025']}%")
    st.markdown(f"**Volatility:** {stock_data['Stock_Volatile_Percentage']}%")
else:
    st.warning("No data available with the selected filters.")
