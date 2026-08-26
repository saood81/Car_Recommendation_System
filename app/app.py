"""
app.py — Streamlit demo for the NLP-powered car recommendation system.

Run locally with:
    streamlit run app.py

The user types a free-text description of what they want in a car, and the app:
  1. Parses hard constraints (budget, seats, fuel type) with rule-based NLP
  2. Embeds the query with Sentence-BERT (or TF-IDF if offline) and ranks all cars
     by semantic similarity to their auto-generated natural-language profile
  3. Combines both into a hybrid score and shows the top matches
  4. Generates a short natural-language explanation of the picks (a simple "AI reply")
"""

import os

import pandas as pd
import streamlit as st

from recommender import load_pipeline, recommend_cars, generate_nl_response

st.set_page_config(page_title="AI Car Recommender (NLP)", page_icon="🚗", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "structured_car_data_cleaned.json")

EXAMPLE_QUERIES = [
    "fuel-efficient family car under $15,000 with good safety",
    "high performance sports car around $60,000",
    "cheap reliable car under $8,000",
    "eco-friendly electric car under $40,000",
]


@st.cache_resource(show_spinner="Loading dataset and building embeddings…")
def get_pipeline():
    return load_pipeline(DATA_PATH)


def main():
    st.title("🚗 AI-Powered Car Recommender")
    st.caption(
        "Describe the car you want in plain English. The system parses your budget, "
        "seat, and fuel preferences, semantically matches your request against 500+ "
        "real car listings, and explains why each pick was chosen."
    )

    df, embedder, car_embeddings = get_pipeline()

    with st.sidebar:
        st.subheader("About this demo")
        st.write(f"**Dataset:** {len(df)} real cars (Comprehensive Vehicle Specifications, Kaggle)")
        st.write(f"**Embedding backend:** {embedder.backend}")
        st.write("---")
        st.write("**Try an example:**")
        for q in EXAMPLE_QUERIES:
            if st.button(q, width='stretch'):
                st.session_state["query"] = q

    query = st.text_input(
        "What are you looking for?",
        value=st.session_state.get("query", ""),
        placeholder="e.g. a spacious family car under $20,000 with great fuel economy",
    )
    top_k = st.slider("Number of recommendations", 3, 10, 5)
    go = st.button("Get Recommendations", type="primary")

    if go and query.strip():
        results, prefs = recommend_cars(query, df, car_embeddings, embedder, top_k=top_k)

        st.subheader("Parsed preferences")
        cols = st.columns(3)
        cols[0].metric("Max budget", f"${prefs['max_budget']:,.0f}" if prefs["max_budget"] else "—")
        cols[1].metric("Min seats", prefs["min_seats"] or "—")
        cols[2].metric("Fuel type", prefs["fuel_type"] or "—")

        st.subheader("AI response")
        st.markdown(generate_nl_response(query, results, prefs))

        st.subheader("Ranked results")
        display_cols = ["make", "model", "price_usd", "fuel_type", "transmission",
                         "mileage_kmpl", "engine_power_hp", "seats", "safety_rating",
                         "semantic_score", "final_score"]
        st.dataframe(
            results[display_cols].rename(columns={
                "price_usd": "Price (USD)", "mileage_kmpl": "Mileage (km/l)",
                "engine_power_hp": "Power (hp)", "safety_rating": "Safety (★)",
                "semantic_score": "Semantic score", "final_score": "Final score",
            }),
            width='stretch',
            hide_index=True,
        )
    elif go:
        st.warning("Type a description of what you're looking for first.")


if __name__ == "__main__":
    main()
