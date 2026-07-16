import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Country Fragility Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading ---
# Use caching to load data only once
@st.cache_data
def load_data(path):
    """Loads the dataset from a CSV file."""
    try:
        df = pd.read_csv(path)
        # Basic cleaning: Convert 'Year' to numeric, coercing errors
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        # Drop rows where 'Year' could not be converted
        df.dropna(subset=['Year'], inplace=True)
        df['Year'] = df['Year'].astype(int)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file was not found at {path}")
        st.info("Please make sure the 'final_strong_dataset.csv' file is in the same folder as your Streamlit script.")
        return None

# Load the data
DATA_PATH = "final_strong_dataset.csv"
df = load_data(DATA_PATH)

# --- Main Application ---
if df is not None:
    # --- Sidebar ---
    st.sidebar.header("Dashboard Controls")
    st.sidebar.markdown("Use the filters below to customize the visualizations.")

    # Year selection
    selected_year = st.sidebar.slider(
        "Select a Year",
        min_value=int(df['Year'].min()),
        max_value=int(df['Year'].max()),
        value=int(df['Year'].max())
    )

    # Country selection (multiselect)
    country_list = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=country_list,
        default=["somalia", "sudan", "afghanistan", "yemen", "syria"]
    )

    # Filter data based on selections
    df_filtered_year = df[df['Year'] == selected_year]
    df_filtered_countries = df[df['Country'].isin(selected_countries)]

    # --- Main Panel ---
    st.title("🌍 Country Fragility and Conflict Dashboard")
    st.markdown(f"Displaying data for the year **{selected_year}**.")

    # --- Key Metrics ---
    st.subheader("Global Snapshot for Selected Year")
    col1, col2, col3 = st.columns(3)
    avg_fragility = df_filtered_year['fragility_score'].mean()
    total_fatalities = df_filtered_year['FATALITIES'].sum()
    total_events = df_filtered_year['EVENTS'].sum()

    col1.metric("Average Fragility Score", f"{avg_fragility:.2f}")
    col2.metric("Total Fatalities", f"{int(total_fatalities):,}")
    col3.metric("Total Conflict Events", f"{int(total_events):,}")

    st.markdown("---")

    # --- Visualizations ---
    st.header("Visualizations")

    # 1. Line Chart: Fragility Score Over Time
    st.subheader("1. Fragility Score Trend for Selected Countries")
    if not selected_countries:
        st.warning("Please select at least one country to see the trend.")
    else:
        fig_line = px.line(
            df_filtered_countries,
            x='Year',
            y='fragility_score',
            color='Country',
            title="Fragility Score Over Time",
            labels={'fragility_score': 'Fragility Score', 'Year': 'Year'},
            markers=True
        )
        fig_line.update_layout(legend_title_text='Country')
        st.plotly_chart(fig_line, use_container_width=True)

    # 2. Bar Chart: Top 10 Most Fragile Countries
    st.subheader(f"2. Top 10 Countries by Fatalities in {selected_year}")
    top_10_fatalities = df_filtered_year.nlargest(10, 'FATALITIES')
    fig_bar = px.bar(
        top_10_fatalities,
        x='Country',
        y='FATALITIES',
        title=f"Top 10 Countries by Total Fatalities in {selected_year}",
        labels={'FATALITIES': 'Total Fatalities', 'Country': 'Country'},
        color='FATALITIES',
        color_continuous_scale=px.colors.sequential.Reds
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Scatter Plot: Economy vs. Security
    st.subheader("3. Economic vs. Political Stability")
    fig_scatter = px.scatter(
        df_filtered_year,
        x='economy',
        y='politics',
        size='fatalities',
        color='Country',
        hover_name='Country',
        title=f"Economy vs. Politics Score in {selected_year}",
        labels={'economy': 'Economy Score', 'politics': 'Politics Score'},
        size_max=60,
        log_x=True,
        log_y=True
    )
    fig_scatter.update_layout(
        xaxis_title="Economy Score (Higher is worse)",
        yaxis_title="Political Score (Higher is worse)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Choropleth Map: Global Fragility Score
    st.subheader(f"4. World Map of Fragility Scores in {selected_year}")
    fig_map = px.choropleth(
        df_filtered_year,
        locations="Country",
        locationmode='country names',
        color="fragility_score",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Global Fragility Scores in {selected_year}"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # --- Raw Data ---
    with st.expander("View Raw Data"):
        st.dataframe(df)

else:
    st.info("Awaiting data file to be loaded...")

