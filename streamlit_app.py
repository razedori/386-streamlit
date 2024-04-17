import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


url = "https://raw.githubusercontent.com/razedori/386-streamlit/main/data2.csv"
df = pd.read_csv(url)

# Sidebar: Top 10 movie ratings
st.sidebar.header("Top 10 Movie Ratings")
year = st.sidebar.selectbox("Select Release Year", sorted(df['release'].unique(), reverse=True))
df_year = df[df['release'] == year][['name', 'my_rating', 'IMDb.Rating']]
imdb_top10 = df_year.nlargest(10, 'IMDb.Rating')
my_top10 = df_year.nlargest(10, 'my_rating').reset_index(drop=True).rename_axis('Position')


st.sidebar.header("Top 10 Movies by IMDb Ratings")
st.sidebar.dataframe(imdb_top10.reset_index(drop=True).rename_axis('Position'))


st.sidebar.header("Top 10 Movies by My Ratings")
st.sidebar.dataframe(my_top10)


st.title("My Movie Data Analysis")
st.write("Welcome to my Streamlit app! Here, I've created some interactive elements where I can explore insights about my movie data. To enhance the analysis, I've also included IMDb ratings to compare with my own ratings for various movies. This is more for personal use but maybe this will inspire you to build your own")

#Main Graph
st.header("Average Ratings Over the Years")
rating_type_avg = st.radio("Select Rating Type for Average Ratings", ["My Rating", "IMDb Rating"])

if rating_type_avg == "My Rating":
    rating_column_avg = 'my_rating'
else:
    rating_column_avg = 'IMDb.Rating'

avg_rating_per_year = df.groupby('release')[rating_column_avg].mean().reset_index()
avg_rating_graph = px.bar(avg_rating_per_year, x='release', y=rating_column_avg, title='Average Ratings Per Year')
avg_rating_graph.update_traces(texttemplate='%{y:.2f}', textposition='outside')
st.plotly_chart(avg_rating_graph)


st.header("Average Ratings by Genre")

df['genres'] = df['genre'].str.split(', ')
df_exploded = df.explode('genres')
genre_avg_rating = df_exploded.groupby('genres')[['IMDb.Rating', 'my_rating']].mean().reset_index()
genre_avg_rating = genre_avg_rating.sort_values(by='my_rating' if rating_type_avg == "My Rating" else 'IMDb.Rating')

#Genre bar graph
st.subheader("Select Rating Type for Genre Analysis")
rating_type_genre = st.radio("Select Rating Type for Genre Bar Graph", ["My Rating", "IMDb Rating"])

if rating_type_genre == "My Rating":
    rating_column_genre = 'my_rating'
else:
    rating_column_genre = 'IMDb.Rating'

genre_avg_rating = genre_avg_rating.sort_values(by=rating_column_genre)

genre_bar_chart = px.bar(genre_avg_rating, x='genres', y=rating_column_genre, title='Average Ratings by Genre')
genre_bar_chart.update_traces(texttemplate='%{y:.2f}', textposition='outside')
st.plotly_chart(genre_bar_chart)

# Table for top 10 by genre 
st.header("Top 10 Highest Rated Movies by Genre")
selected_genre = st.selectbox("Select Genre", df['genres'].explode().unique())

st.subheader("Select Rating Type for Genre Table")
rating_type_table = st.radio("Select Type of rating", ["My Rating", "IMDb Rating"])

if rating_type_table == "My Rating":
    rating_column_table = 'my_rating'
else:
    rating_column_table = 'IMDb.Rating'

top_genre_movies = df[(df['genres'].apply(lambda x: selected_genre in x)) & (df[rating_column_table].notnull())][['name', rating_column_table,'release']]
top_genre_movies = top_genre_movies.nlargest(10, rating_column_table).reset_index(drop=True)
st.dataframe(top_genre_movies, width=800)

# Day of the week part
day_of_week_stats = df.groupby('watch_day_of_week').agg({'name': 'count', 'my_rating': 'mean'}).reset_index()
day_of_week_stats = day_of_week_stats.rename(columns={'name': 'movies_watched', 'my_rating': 'avg_rating'})


fig = make_subplots(specs=[[{"secondary_y": True}]])


fig.add_trace(go.Bar(x=day_of_week_stats['watch_day_of_week'], y=day_of_week_stats['movies_watched'], 
                     name='Movies Watched', marker=dict(color='skyblue')), 
              secondary_y=False)


fig.add_trace(go.Scatter(x=day_of_week_stats['watch_day_of_week'], y=day_of_week_stats['avg_rating'], 
                         mode='lines', name='Average Rating', line=dict(color='orange')),
              secondary_y=True)


fig.update_layout(title='Number of Movies Watched and Average Rating per Day of the Week',
                  xaxis=dict(title='Day of the Week'),
                  yaxis=dict(title='Movies Watched', side='left', color='skyblue'),
                  yaxis2=dict(title='Average Rating', side='right', overlaying='y', color='orange'))

st.plotly_chart(fig)