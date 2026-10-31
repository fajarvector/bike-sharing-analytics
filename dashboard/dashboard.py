import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Dapatkan lokasi direktori tempat file dashboard.py berada
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "hour.csv")

# Mengatur style seaborn
sns.set_theme(style='darkgrid')



# Helper Functions
def create_daily_sharing_df(df):
    return df.groupby(by='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()

def create_hourly_workday_df(df):
    return df.groupby(by=['workingday', 'hr'])['cnt'].mean().reset_index()

def create_weather_impact_df(df):
    def group_weather(w):
        if w == 1:
            return 'Cerah'
        elif w == 2:
            return 'Mendung/Berkabut'
        else:
            return 'Cuaca Buruk'
    df_copy = df.copy()
    df_copy['weather_group'] = df_copy['weathersit'].apply(group_weather)
    return df_copy.groupby(by=['weather_group'])[['casual', 'registered', 'cnt']].mean().reset_index()

def create_season_yr_df(df):
    daily_sum = df.groupby(by=['dteday', 'yr', 'season_label'])['cnt'].sum().reset_index()
    return daily_sum.groupby(by=['yr', 'season_label'])['cnt'].mean().reset_index()

def get_lowest_season(df):
    daily_season = df.groupby(['dteday', 'season_label'])['cnt'].sum().reset_index()
    if not daily_season.empty:
        return daily_season.groupby('season_label')['cnt'].mean().idxmin()
    return "-"

# Memuat dan preprocessing data
all_df = pd.read_csv(file_path)
all_df["dteday"] = pd.to_datetime(all_df["dteday"])
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
all_df["season_label"] = all_df["season"].map(season_mapping)

# Side bar dan filter
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

Python
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=100)
    st.title("Capital Bikeshare")
    
    # Menerima input tanggal
    date_input = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Try-Except block sesuai saran reviewer
    try:
        start_date, end_date = date_input
    except ValueError:
        st.error("Peringatan: Harap pilih tanggal akhir (End Date) untuk melanjutkan.")
        st.stop() # Menghentikan eksekusi kode di bawahnya hingga user memilih 2 tanggal

# (Kode main_df filtering tetap berada di bawahnya)
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

# Eksekusi Agregasi Data
daily_sharing_df = create_daily_sharing_df(main_df)
hourly_workday_df = create_hourly_workday_df(main_df)
weather_impact_df = create_weather_impact_df(main_df)
season_yr_df = create_season_yr_df(main_df)

# ==========================================
# DASHBOARD MAIN PAGE
# ==========================================
st.header('Bike Sharing Analytics Dashboard 🚲')

st.subheader('Daily Rentals Summary')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rides", value=f"{daily_sharing_df['cnt'].sum():,}")
with col2:
    st.metric("Registered Users", value=f"{daily_sharing_df['registered'].sum():,}")
with col3:
    st.metric("Casual Users", value=f"{daily_sharing_df['casual'].sum():,}")
st.divider()

# -----------------------------------------------------------
# 1. PERTANYAAN 1
# -----------------------------------------------------------
st.subheader("1. Rata-rata Penyewaan per Jam (Hari Kerja vs Libur 2011-2012)")

workday_df = hourly_workday_df[hourly_workday_df['workingday'] == 1]
weekend_df = hourly_workday_df[hourly_workday_df['workingday'] == 0]

peak_workday = workday_df.loc[workday_df['cnt'].idxmax(), 'hr'] if not workday_df.empty else 0
peak_weekend = weekend_df.loc[weekend_df['cnt'].idxmax(), 'hr'] if not weekend_df.empty else 0

col1, col2 = st.columns(2)
col1.metric("Volume Tertinggi (Hari Kerja)", f"{int(peak_workday)}:00 WIB")
col2.metric("Volume Tertinggi (Akhir Pekan)", f"{int(peak_weekend)}:00 WIB")

fig1, ax1 = plt.subplots(figsize=(16, 8))
sns.lineplot(x="hr", y="cnt", hue="workingday", data=hourly_workday_df, marker="o", linewidth=3, palette=["#FF9F00", "#90CAF9"], ax=ax1)
ax1.set_title("Perbandingan Rata-rata Peminjaman per Jam", fontsize=20)
ax1.set_ylabel("Rata-rata Penyewaan", fontsize=15)
ax1.set_xlabel("Jam Operasi (0-23)", fontsize=15)
ax1.set_xticks(range(0, 24))
plt.legend(title='Keterangan', labels=['Akhir Pekan/Libur', 'Hari Kerja'], fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig1)

st.info(f"**Bahan Pertimbangan:** Data historis menunjukkan jam puncak terjadi pada pukul {int(peak_workday)}:00 di hari kerja dan pukul {int(peak_weekend)}:00 pada hari libur. Penjadwalan redistribusi armada dapat difokuskan sebelum jam tersebut.")
st.divider()

# -----------------------------------------------------------
# 2. PERTANYAAN 2
# -----------------------------------------------------------
st.subheader("2. Perbedaan Rata-rata Sewa per Jam Berdasarkan Cuaca (2011-2012)")

try:
    val_clear_casual = weather_impact_df[weather_impact_df['weather_group'] == 'Cerah']['casual'].values[0]
    val_bad_casual = weather_impact_df[weather_impact_df['weather_group'] == 'Cuaca Buruk']['casual'].values[0]
    drop_casual = ((val_clear_casual - val_bad_casual) / val_clear_casual) * 100
    
    val_clear_reg = weather_impact_df[weather_impact_df['weather_group'] == 'Cerah']['registered'].values[0]
    val_bad_reg = weather_impact_df[weather_impact_df['weather_group'] == 'Cuaca Buruk']['registered'].values[0]
    drop_reg = ((val_clear_reg - val_bad_reg) / val_clear_reg) * 100
except (IndexError, ZeroDivisionError):
    drop_casual, drop_reg = 0, 0

col1, col2 = st.columns(2)
col1.metric("Penurunan Casual (Cerah vs Cuaca Buruk)", f"-{drop_casual:.1f}%", delta_color="inverse")
col2.metric("Penurunan Registered (Cerah vs Cuaca Buruk)", f"-{drop_reg:.1f}%", delta_color="inverse")

# Melt data agar formatnya persis dengan visualisasi seaborn di Notebook
weather_melt = weather_impact_df.melt(
    id_vars=['weather_group'], 
    value_vars=['casual', 'registered'], 
    var_name='Tipe Pengguna', 
    value_name='Rata-rata Sewa per Jam'
)

fig2, ax2 = plt.subplots(figsize=(12, 6))
# Order dipastikan sama persis dengan Notebook
sns.barplot(
    data=weather_melt, 
    x='weather_group', 
    y='Rata-rata Sewa per Jam', 
    hue='Tipe Pengguna', 
    palette=["#90CAF9", "#FF9F00"], 
    order=['Cerah', 'Mendung/Berkabut', 'Cuaca Buruk'], 
    ax=ax2
)
ax2.set_title("Rata-rata Penyewaan per Jam (Cerah vs Cuaca Buruk)", fontsize=16)
ax2.set_xlabel("Kondisi Cuaca", fontsize=12)
ax2.set_ylabel("Rata-rata Peminjaman per Jam", fontsize=12)
st.pyplot(fig2)

st.info("**Bahan Pertimbangan:** Terdapat perbedaan rata-rata yang lebih signifikan pada pengguna *casual* saat cuaca buruk. Ini dapat menjadi acuan strategi operasional spesifik saat cuaca berubah.")

# -----------------------------------------------------------
# 3. PERTANYAAN 3
# -----------------------------------------------------------
st.subheader("3. Pertumbuhan Rata-rata Harian per Musim (2011 vs 2012)")

try:
    avg_2011 = season_yr_df[season_yr_df['yr'] == 0]['cnt'].mean()
    avg_2012 = season_yr_df[season_yr_df['yr'] == 1]['cnt'].mean()
    growth = ((avg_2012 - avg_2011) / avg_2011) * 100
except (IndexError, ZeroDivisionError):
    growth = 0

lowest_season_name = get_lowest_season(main_df)

col1, col2 = st.columns(2)
col1.metric("Peningkatan Rata-rata (2011 ke 2012)", f"+{growth:.1f}%")
col2.metric("Musim dengan Rata-rata Terendah", lowest_season_name)

season_yr_df['Tahun'] = season_yr_df['yr'].map({0: '2011', 1: '2012'})
fig3, ax3 = plt.subplots(figsize=(16, 8))
sns.barplot(data=season_yr_df, x='season_label', y='cnt', hue='Tahun', palette=["#D3D3D3", "#90CAF9"], ax=ax3)
ax3.set_title("Rata-rata Penyewaan Harian per Musim", fontsize=20)
ax3.set_xlabel("Musim", fontsize=15)
ax3.set_ylabel("Rata-rata Penyewaan Harian", fontsize=15)
st.pyplot(fig3)

st.info(f"**Bahan Pertimbangan:** Data historis menunjukkan musim **{lowest_season_name}** memiliki rata-rata penyewaan terendah, sehingga waktu ini dapat dipertimbangkan sebagai periode perbaikan armada untuk meminimalisasi kendala ketersediaan.")

st.caption('Dashboard oleh Fajar Nurhidayat')