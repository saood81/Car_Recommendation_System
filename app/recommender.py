"""
recommender.py — Core NLP car recommendation engine.

Loads the real, messy scraped car dataset (JSON), repairs a documented column-shift
defect via content-pattern extraction, builds natural-language car profiles, and
ranks cars against a free-text user query using a hybrid semantic + hard-constraint
scoring approach.

This module has NO Streamlit dependency so it can be reused from the notebook, a CLI,
or tests.
"""

import json
import os
import re

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

USD_PER_INR = 1 / 83.0  # approximate INR->USD conversion rate

FUEL_KEYWORDS = {
    "electric": "Electric", "ev": "Electric",
    "hybrid": "Hybrid",
    "diesel": "Diesel",
    "petrol": "Petrol", "gas": "Petrol", "gasoline": "Petrol",
    "cng": "CNG",
}

WORD_NUMBERS = {
    "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
}

KNOWN_MULTIWORD_MAKES = [
    "Maruti Suzuki", "Aston Martin", "Land Rover", "Mercedes-Benz", "Mercedes Benz",
    "Rolls-Royce", "Rolls Royce", "Alfa Romeo", "MG Motor", "San Motors",
]


# ---------------------------------------------------------------------------
# Data loading & repair
# ---------------------------------------------------------------------------

def field_blob(record: dict) -> str:
    """Concatenate all non-null field values into one text blob for pattern search."""
    return " | ".join(str(v) for v in record.values() if v)


def extract_price_usd(text: str) -> float:
    m = re.search(r"Rs\.?\s*([\d,.]+)\s*(?:-\s*([\d,.]+)\s*)?(Lakh|Cr)", text, re.I)
    if not m:
        return np.nan
    lo = float(m.group(1).replace(",", ""))
    hi = float(m.group(2).replace(",", "")) if m.group(2) else lo
    multiplier = 10_000_000 if m.group(3).lower() == "cr" else 100_000  # INR
    avg_inr = ((lo + hi) / 2) * multiplier
    return round(avg_inr * USD_PER_INR, 2)


def extract_float(pattern: str, text: str) -> float:
    m = re.search(pattern, text, re.I)
    return float(m.group(1)) if m else np.nan


def extract_keyword_by_position(keywords, text: str):
    """Return the keyword appearing EARLIEST in the text — the true primary value —
    rather than the first one checked, avoiding bias e.g. 'Petrol/CNG' -> 'CNG'."""
    matches = []
    for kw in keywords:
        m = re.search(rf"\b{kw}\b", text, re.I)
        if m:
            matches.append((m.start(), kw))
    return sorted(matches)[0][1] if matches else None


def extract_safety_star(text: str) -> float:
    m = re.search(r"(\d)\s*Star Safety", text, re.I)
    return int(m.group(1)) if m else np.nan


def extract_seats(text: str) -> float:
    nums = re.findall(r"(\d+)\s*Seats", text, re.I)
    return int(max(int(n) for n in nums)) if nums else np.nan


def extract_make(name: str) -> str:
    for mk in KNOWN_MULTIWORD_MAKES:
        if name.startswith(mk):
            return mk
    return name.split(" ")[0]


def parse_record(r: dict) -> dict:
    text = field_blob(r)
    name = r.get("name", "")
    make = extract_make(name)
    return {
        "name": name,
        "make": make,
        "model": name[len(make):].strip() or name,
        "price_usd": extract_price_usd(text),
        "engine_cc": extract_float(r"(\d{2,5})\s*cc", text),
        "engine_power_hp": extract_float(r"([\d.]+)\s*bhp", text),
        "mileage_kmpl": extract_float(r"([\d.]+)\s*kmpl", text),
        "fuel_type": extract_keyword_by_position(
            ["Electric", "Hybrid", "CNG", "LPG", "Diesel", "Petrol"], text
        ),
        "transmission": extract_keyword_by_position(
            ["Automatic", "Manual", "CVT", "AMT", "DCT"], text
        ),
        "safety_rating": extract_safety_star(text),
        "seats": extract_seats(text),
    }


def load_and_clean(json_path: str) -> pd.DataFrame:
    with open(json_path) as f:
        raw_records = json.load(f)

    df = pd.DataFrame([parse_record(r) for r in raw_records])
    df = df.dropna(subset=["price_usd"]).copy()

    numeric_cols = ["engine_cc", "engine_power_hp", "mileage_kmpl", "seats", "safety_rating"]
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    df["seats"] = df["seats"].round().clip(2, 9).astype(int)
    df["safety_rating"] = df["safety_rating"].round().clip(1, 5).astype(int)
    df["fuel_type"] = df["fuel_type"].fillna("Unknown")
    df["transmission"] = df["transmission"].fillna("Unknown")

    for col in ["price_usd", "mileage_kmpl", "engine_power_hp", "engine_cc"]:
        lo, hi = df[col].quantile([0.01, 0.99])
        df[col] = df[col].clip(lo, hi)

    df = df.reset_index(drop=True)
    df["car_id"] = df.index
    df["car_profile"] = df.apply(build_car_profile, axis=1)
    return df


def build_car_profile(row) -> str:
    return (
        f"{row['make']} {row['model']} is priced at ${row['price_usd']:,.0f}. "
        f"It runs on {row['fuel_type'].lower()} fuel with a "
        f"{row['transmission'].lower()} transmission, has a {row['engine_cc']:.0f}cc "
        f"engine producing {row['engine_power_hp']:.0f} horsepower, achieves "
        f"{row['mileage_kmpl']:.1f} km/l fuel efficiency, seats {row['seats']} people, "
        f"and has a {row['safety_rating']}-star safety rating."
    )


# ---------------------------------------------------------------------------
# NLP preference parsing
# ---------------------------------------------------------------------------

def parse_user_preferences(text: str) -> dict:
    text_l = text.lower()
    prefs = {"max_budget": None, "min_seats": None, "fuel_type": None}

    for m in re.finditer(
        r"(under|below|less than|budget of|around|no more than|not more than|"
        r"up to|max(?:imum)? of|max(?:imum)?)\s+\$?\s?(\d[\d,]*)\s?(k)?",
        text_l,
    ):
        amount = float(m.group(2).replace(",", ""))
        if m.group(3) == "k":
            amount *= 1000
        prefs["max_budget"] = amount

    for word, num in WORD_NUMBERS.items():
        text_l = re.sub(rf"\b{word}\b(?=\s?-?\s?seat)", str(num), text_l)

    seat_match = re.search(r"(\d)\s?(-)?\s?seat", text_l)
    if seat_match:
        prefs["min_seats"] = int(seat_match.group(1))
    elif "family" in text_l:
        prefs["min_seats"] = 5

    for kw, val in FUEL_KEYWORDS.items():
        if kw in text_l:
            prefs["fuel_type"] = val
            break

    return prefs


# ---------------------------------------------------------------------------
# Embeddings (Sentence-BERT with TF-IDF fallback)
# ---------------------------------------------------------------------------

class Embedder:
    """Wraps Sentence-BERT if available, else falls back to TF-IDF so the app still
    works offline. Exposes a uniform .encode(list[str]) -> np.ndarray interface."""

    def __init__(self):
        self.backend = None
        self._tfidf = None
        self._tfidf_fitted = False
        self._st_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.backend = "sentence-transformers (all-MiniLM-L6-v2)"
        except Exception as e:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._tfidf = TfidfVectorizer()
            self.backend = f"TF-IDF (fallback: {e})"

    def encode(self, texts):
        if self._st_model is not None:
            return self._st_model.encode(
                texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
            )
        from sklearn.preprocessing import normalize as sk_normalize
        if not self._tfidf_fitted:
            vecs = self._tfidf.fit_transform(texts).toarray()
            self._tfidf_fitted = True
        else:
            vecs = self._tfidf.transform(texts).toarray()
        return sk_normalize(vecs)


# ---------------------------------------------------------------------------
# Hybrid recommender
# ---------------------------------------------------------------------------

def recommend_cars(user_text, df, car_embeddings, embedder, top_k=5,
                    w_semantic=0.7, w_budget=0.3):
    prefs = parse_user_preferences(user_text)

    query_emb = embedder.encode([user_text])
    sim_scores = cosine_similarity(query_emb, car_embeddings)[0]

    candidates = df.copy()
    candidates["semantic_score"] = sim_scores

    penalty = np.zeros(len(candidates))
    if prefs["max_budget"]:
        penalty += (candidates["price_usd"] > prefs["max_budget"]) * 0.5
    if prefs["min_seats"]:
        penalty += (candidates["seats"] < prefs["min_seats"]) * 0.3
    if prefs["fuel_type"]:
        penalty += (candidates["fuel_type"] != prefs["fuel_type"]) * 0.2

    if prefs["max_budget"]:
        budget_fit = 1 - (candidates["price_usd"] / prefs["max_budget"]).clip(0, 2) / 2
    else:
        budget_fit = 1 - (candidates["price_usd"] - candidates["price_usd"].min()) / \
                         (candidates["price_usd"].max() - candidates["price_usd"].min() + 1e-9)

    candidates["final_score"] = (
        w_semantic * candidates["semantic_score"] + w_budget * budget_fit - penalty
    )

    # Sort by final_score and deduplicate to ensure diverse results
    sorted_candidates = candidates.sort_values("final_score", ascending=False)
    
    # Keep only the first occurrence of each unique car (by make + model)
    seen = set()
    unique_indices = []
    for idx, row in sorted_candidates.iterrows():
        car_key = (row["make"], row["model"])
        if car_key not in seen:
            seen.add(car_key)
            unique_indices.append(idx)
            if len(unique_indices) >= top_k:
                break
    
    results = sorted_candidates.loc[unique_indices]
    return results, prefs


# ---------------------------------------------------------------------------
# Natural-language response generation (template-based "AI reply")
# ---------------------------------------------------------------------------

def generate_nl_response(user_text: str, results: pd.DataFrame, prefs: dict) -> str:
    """Turns the ranked results into a short natural-language explanation, so the
    system 'talks back' rather than just showing a table."""
    if results.empty:
        return "I couldn't find any cars matching that request — try loosening your budget or constraints."

    constraint_bits = []
    if prefs.get("max_budget"):
        constraint_bits.append(f"a budget around ${prefs['max_budget']:,.0f}")
    if prefs.get("min_seats"):
        constraint_bits.append(f"at least {prefs['min_seats']} seats")
    if prefs.get("fuel_type"):
        constraint_bits.append(f"{prefs['fuel_type']} fuel")
    constraint_txt = (" with " + ", ".join(constraint_bits)) if constraint_bits else ""

    lines = [f"Based on your request for \"{user_text}\"{constraint_txt}, here's what I'd recommend:\n"]

    for i, (_, row) in enumerate(results.iterrows(), start=1):
        why_bits = []
        if prefs.get("max_budget") and row["price_usd"] <= prefs["max_budget"]:
            why_bits.append("fits your budget")
        if prefs.get("min_seats") and row["seats"] >= prefs["min_seats"]:
            why_bits.append(f"seats {row['seats']}")
        if row["mileage_kmpl"] >= 18:
            why_bits.append("strong fuel efficiency")
        if row["engine_power_hp"] >= 200:
            why_bits.append("high performance")
        if row["safety_rating"] >= 4:
            why_bits.append(f"{row['safety_rating']}-star safety")
        why_txt = ", ".join(why_bits) if why_bits else "a good overall match for your query"

        lines.append(
            f"{i}. **{row['make']} {row['model']}** — ${row['price_usd']:,.0f}, "
            f"{row['fuel_type']}, {row['mileage_kmpl']:.1f} km/l, "
            f"{row['engine_power_hp']:.0f} hp, {row['seats']} seats "
            f"({row['safety_rating']}★ safety). Recommended because it {why_txt}."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Convenience loader used by the app / CLI
# ---------------------------------------------------------------------------

def load_pipeline(json_path: str):
    df = load_and_clean(json_path)
    embedder = Embedder()
    car_embeddings = embedder.encode(df["car_profile"].tolist())
    return df, embedder, car_embeddings
