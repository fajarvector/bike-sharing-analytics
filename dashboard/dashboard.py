import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Dapatkan lokasi direktori tempat file dashboard.py berada
current_dir = os.path.dirname(os.path.abspath(__file__))

# Gabungkan lokasi direktori tersebut dengan nama file CSV
file_path = os.path.join(current_dir, "hour.csv")

# Mengatur style seaborn
sns.set_theme(style='darkgrid')

def create_daily_sharing_df(df):
    daily_df = df.groupby(by='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    return daily_df

def create_by_season_df(df):
    season_df = df.groupby(by="season_label")['cnt'].sum().reset_index()
    season_df = season_df.sort_values(by="cnt", ascending=False)
    return season_df

def create_by_weather_df(df):
    weather_df = df.groupby(by="weather_label")['cnt'].sum().reset_index()
    weather_df = weather_df.sort_values(by="cnt", ascending=False)
    return weather_df

def create_by_hour_df(df):
    hourly_df = df.groupby(by="hr")['cnt'].mean().reset_index()
    return hourly_df


# Memuat dan preprocessing data
all_df = pd.read_csv(file_path)

all_df["dteday"] = pd.to_datetime(all_df["dteday"])
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_mapping = {1: "Clear", 2: "Cloudy/Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}

all_df["season_label"] = all_df["season"].map(season_mapping)
all_df["weather_label"] = all_df["weathersit"].map(weather_mapping)


# Side bar dan filter
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=100)
    st.title("Capital Bikeshare")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

daily_sharing_df = create_daily_sharing_df(main_df)
season_df = create_by_season_df(main_df)
weather_df = create_by_weather_df(main_df)
hourly_df = create_by_hour_df(main_df)

# Dashboard dan Main Page
st.header('Bike Sharing Analytics Dashboard 🚲')

st.subheader('Daily Rentals Summary')
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = daily_sharing_df['cnt'].sum()
    st.metric("Total Rides", value=f"{total_rentals:,}")

with col2:
    total_registered = daily_sharing_df['registered'].sum()
    st.metric("Registered Users", value=f"{total_registered:,}")

with col3:
    total_casual = daily_sharing_df['casual'].sum()
    st.metric("Casual Users", value=f"{total_casual:,}")

st.subheader("Daily Rentals Trend")
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_sharing_df["dteday"],
    daily_sharing_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Total Bike Rentals Over Time", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Rentals by Season & Weather")
col1, col2 = st.columns(2)

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        y="cnt", 
        x="season_label",
        data=season_df,
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Rentals by Season", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        y="cnt", 
        x="weather_label",
        data=weather_df,
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Rentals by Weather", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

st.subheader("Average Hourly Rentals")
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(
    x="hr",
    y="cnt",
    data=hourly_df,
    marker="o",
    linewidth=3,
    color="#FF9F00",
    ax=ax
)
ax.set_title("Peak Hours Analysis", loc="center", fontsize=20)
ax.set_ylabel("Average Rentals", fontsize=15)
ax.set_xlabel("Hour of the Day (0-23)", fontsize=15)
ax.set_xticks(range(0, 24))
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Grid
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)

st.caption('Dashboard oleh Fajar Nurhidayat')