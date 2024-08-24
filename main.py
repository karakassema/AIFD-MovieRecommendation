import streamlit as st
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import json
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Define movie genres and languages
genres = [
    'Aksiyon', 'Komedi', 'Drama', 'Bilim Kurgu',
    'Korku', 'Romantik', 'Western', 'Animasyon',
    'Belgesel', 'Suç Filmi', 'Tarih', 'Anime'
]

languages = [
    'English', 'Türkçe', 'Français',
    'Deutsch', 'Español', 'Italiano',
    '日本語', '한국어', '中文'
]


def get_movie_recommendations(selected_genres, favorite_movies, selected_languages):
    prompt = f"Suggest 5 movies based on the following genres: {', '.join(selected_genres)}. "
    prompt += f"The user's favorite movies are: {', '.join(favorite_movies)}. "
    prompt += f"The user's preferred languages are: {', '.join(selected_languages)}. "
    prompt += "Provide the results in the following format: Movie Name | Genre | Short Summary"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that recommends movies."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        temperature=0.7,
    )

    recommendations = response.choices[0].message.content.strip().split('\n')
    return [movie.split('|') for movie in recommendations if '|' in movie]


def save_recommendations(recommendations, user_input):
    try:
        if os.path.exists('recommendations.json'):
            with open('recommendations.json', 'r') as f:
                content = f.read()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        else:
            data = []

        new_entry = {
            "user_input": user_input,
            "recommendations": recommendations
        }
        data.append(new_entry)

        with open('recommendations.json', 'w') as f:
            json.dump(data, f)
    except json.JSONDecodeError:

        data = []
        new_entry = {
            "user_input": user_input,
            "recommendations": recommendations
        }
        data.append(new_entry)
        with open('recommendations.json', 'w') as f:
            json.dump(data, f)


def load_recommendations():
    try:
        if os.path.exists('recommendations.json'):
            with open('recommendations.json', 'r') as f:
                content = f.read()
                if content:
                    return json.loads(content)
    except json.JSONDecodeError:
        pass
    return []


# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f0f0;
        padding: 20px;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .header {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .content {
        background-color: #ffffe0;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .results {
        background-color: #e6f3ff;
        padding: 20px;
        border-radius: 10px;
    }
    .submit-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stDataFrame {
        width: 100%;



    }
    .stDataFrame td, .stDataFrame th {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    .stDataFrame table {
        background-color: #e6f3ff !important;
    }
    .stDataFrame th {
        background-color: #4a86e8 !important;
        color: white !important;
    }
    .stDataFrame td {
        background-color: #e6f3ff !important;
    }
    

    .icon {
        font-size: 18px;
        margin-right: 5px;
    }
    .instructions {
        list-style: none;
        padding-left: 0;
    }
    .instructions li {
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit app
st.title("Film Öneri Sistemi")
st.markdown('---')
st.subheader("Nasıl Çalışır?")
st.markdown('---')
st.markdown("""
<ul class="instructions">
    <li><span class="icon">✏️</span>Sevdiğiniz film türlerini seçin</li>
    <li><span class="icon">✏️</span>En sevdiğiniz 3 filmi belirtin</li>
    <li><span class="icon">✏️</span>Bilgileri gönderin</li>
    <li><span class="icon">✏️</span>Size özel film önerileri alın!</li>
</ul>""", unsafe_allow_html=True)

# User input
st.subheader("Film Türleri")
genre_cols = st.columns(3)
selected_genres = []
for i, genre in enumerate(genres):
    col_index = i % 3
    with genre_cols[col_index]:
        if st.checkbox(genre, key=f"genre_{genre}"):
            selected_genres.append(genre)

st.subheader("Tercih Edilen Diller")
language_cols = st.columns(3)
selected_languages = []
for i, language in enumerate(languages):
    col_index = i % 3
    with language_cols[col_index]:
        if st.checkbox(language, key=f"lang_{language}"):
            selected_languages.append(language)

st.subheader("En Sevdiğiniz 3 Film")
favorite_movies = [
    st.text_input(label="1. Film", placeholder="1. Film"),
    st.text_input(label="2. Film", placeholder="2. Film"),
    st.text_input(label="3. Film", placeholder="3. Film")
]

if st.button("Öneriler Al", key="submit", help="Click to get recommendations"):
    if selected_genres and selected_languages and all(favorite_movies):
        recommendations = get_movie_recommendations(selected_genres, favorite_movies, selected_languages)

        user_input = {
            "genres": selected_genres,
            "languages": selected_languages,
            "favorite_movies": favorite_movies
        }

        save_recommendations(recommendations, user_input)

        st.subheader("Önerilen Filmler")
        df = pd.DataFrame(recommendations, columns=["Film Adı", "Tür", "Kısa Özet"])
        st.dataframe(df, hide_index=True)
    else:
        st.warning("Lütfen en az bir tür seçin, en az bir dil seçin ve üç favori film girin.")

# Buttons for showing/hiding previous recommendations
col1, col2 = st.columns(2)
show_button = col1.button("Önceki Önerileri Göster")
hide_button = col2.button("Önceki Önerileri Gizle")

if 'show_previous' not in st.session_state:
    st.session_state.show_previous = False

if show_button:
    st.session_state.show_previous = True
if hide_button:
    st.session_state.show_previous = False

# Display previous recommendations
if st.session_state.show_previous:
    st.subheader("Önceki Öneriler")
    previous_recommendations = load_recommendations()
    if not previous_recommendations:
        st.info("Henüz geçmiş öneri bulunmamaktadır.")
    else:
        for i, entry in enumerate(reversed(previous_recommendations), 1):
            st.markdown(f"**Öneri {i}**")
            st.markdown("**Kullanıcı Seçimleri:**")
            user_input = entry["user_input"]
            user_df = pd.DataFrame({
                "Seçilen Türler": [", ".join(user_input["genres"])],
                "Tercih Edilen Diller": [", ".join(user_input["languages"])],
                "Favori Filmler": [", ".join(user_input["favorite_movies"])]
            })
            st.dataframe(user_df, hide_index=True, use_container_width=True)

            st.markdown("**Önerilen Filmler:**")
            df = pd.DataFrame(entry["recommendations"], columns=["Film Adı", "Tür", "Kısa Özet"])
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.markdown("---")