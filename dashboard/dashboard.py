import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from babel.numbers import format_currency
sns.set(style='dark')


def create_renters_hour_df(hour_df):
    renters_hour_df = hour_df.groupby(by="hr").agg({
        "cnt": "sum"
    })
    return renters_hour_df


def create_renters_day_df(day_df):
    renters_day_df = day_df.query(
        str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return renters_day_df


def create_sum_registered_df(day_df):
    sum_registered_df = day_df.groupby(by="dteday").agg({
        "registered": "sum"
    })
    sum_registered_df = sum_registered_df.reset_index()
    sum_registered_df.rename(columns={
        "registered": "sum_registered",
    }, inplace=True)
    return sum_registered_df


def create_sum_casual_df(day_df):
    sum_casual_df = day_df.groupby(by="dteday").agg({
        "casual": "sum"
    })
    sum_casual_df = sum_casual_df.reset_index()
    sum_casual_df.rename(columns={
        "casual": "sum_casual",
    }, inplace=True)
    return sum_casual_df


def create_sum_renters_df(hour_df):
    renters_df = hour_df.groupby("hr").cnt.sum(
    ).sort_values(ascending=False).reset_index()
    return renters_df


def create_renters_season_df(day_df):
    season_df = day_df.groupby(by="season").cnt.sum().reset_index()
    return season_df


day_df = pd.read_csv("day_data.csv")
hour_df = pd.read_csv("hour_data.csv")

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)


for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

min_day = day_df["dteday"].min()
max_day = day_df["dteday"].max()
min_hour = hour_df["dteday"].min()
max_hour = hour_df["dteday"].max()


with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://previews.123rf.com/images/stacyl17/stacyl171912/stacyl17191200104/135618701-vector-illustration-of-bike-rental-brush-lettering-for-banner-leaflet-poster-clothes-logo.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Span',
        min_value=min_day,
        max_value=max_day,
        value=[min_day, max_day]
    )

main_day_df = day_df[(day_df["dteday"] >= str(start_date)) &
                     (day_df["dteday"] <= str(end_date))]
main_hour_df = hour_df[(day_df["dteday"] >= str(start_date)) &
                       (hour_df["dteday"] <= str(end_date))]

hour_renters_df = create_renters_hour_df(main_hour_df)
renters_day_df = create_renters_day_df(main_day_df)
sum_registered_df = create_sum_registered_df(main_day_df)
sum_casual_df = create_sum_casual_df(main_day_df)
sum_renters_df = create_sum_renters_df(main_hour_df)
seasons_df = create_renters_season_df(main_hour_df)

st.header(':bike: Bike-sharing Dashboard')

col1, col2, col3 = st.columns(3)

with col1:
    total_renters = renters_day_df.cnt.sum()
    st.metric("Total Bike Sharing Renters", value=total_renters)

with col2:
    total_casual_renters = sum_casual_df.sum_casual.sum()
    st.metric("Total Casual Renters", value=total_casual_renters)

with col3:
    total_registered_renters = sum_registered_df.sum_registered.sum()
    st.metric("Total Registered Renters", value=total_registered_renters)

st.markdown("---")

st.subheader("Number of Rentals from 2011 to 2012")
fig, ax = plt.subplots(figsize=(20, 8))

sns.lineplot(
    x=day_df["dteday"],
    y=day_df["cnt"],
    marker='o',
    linewidth=2,
    color="#FF5733"
)

plt.title("Number of Rentals from 2011 to 2012", loc="center", fontsize=20)
plt.xlabel("Year-Month", fontsize=14)
plt.ylabel("Renters of Bike Sharing", fontsize=14)

plt.tick_params(axis='y', labelsize=20)
plt.tick_params(axis='x', labelsize=15)

plt.xticks(rotation=45)

plt.grid(True)
plt.show()
st.pyplot(fig)

st.subheader("Comparison of Bike Rentals between Registered and Casual Users")
user_type_rentals = day_df[['registered', 'casual']].sum().reset_index()
user_type_rentals.columns = ['user_type', 'total_rentals']

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='user_type', y='total_rentals',
            data=user_type_rentals, color='skyblue')
plt.title('Comparison of Bike Rentals between Registered and Casual Users')
plt.xlabel('User Type')
plt.ylabel('Total Rentals')
plt.show()
st.pyplot(fig)

st.subheader("Daily Average Bike Rentals: Registered vs. Casual Users")
daily_average_rentals = day_df[['dteday', 'registered', 'casual']].set_index(
    'dteday').resample('D').mean()
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=daily_average_rentals, palette='viridis', linewidth=2.5)
plt.title('Daily Average Bike Rentals: Registered vs. Casual Users')
plt.xlabel('Date')
plt.ylabel('Average Daily Rentals')
plt.legend(labels=['Registered Users', 'Casual Users'])
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
st.pyplot(fig)

st.subheader("Average Casual Bike Rentals by Weekday")
average_casual_weekday = day_df.groupby('weekday', observed=True)[
    'casual'].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='weekday', y='casual', hue='weekday',
            data=average_casual_weekday, palette='coolwarm', dodge=False, legend=False)
plt.title('Average Casual Bike Rentals by Weekday')
plt.xlabel('Day of the Week')
plt.ylabel('Average Casual Rentals')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()
st.pyplot(fig)

st.subheader("Total Bike Rentals by Season and Weather Condition")
season_weather_rentals = day_df.groupby(['season', 'weathersit'], observed=True)['cnt'].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='season', y='cnt', hue='weathersit', data=season_weather_rentals, palette='Set2')
plt.title('Total Bike Rentals by Season and Weather Condition')
plt.xlabel('Season')
plt.ylabel('Total Rentals')
plt.legend(title='Weather Condition')
plt.grid(axis='y')
plt.show()
st.pyplot(fig)

st.caption(':copyright: Nisirna Aprilia Kamila')
