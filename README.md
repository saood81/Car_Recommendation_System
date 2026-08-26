# AI-Powered Car Recommendation System Using NLP

An NLP-based hybrid recommendation system that matches a user's free-text description
of the car they want (budget, usage, fuel efficiency, performance) against a real
dataset of car specifications, using semantic sentence embeddings combined with
rule-based constraint filtering.

> Course project — see `docs/report.docx` (or `docs/report.pdf`) for the full 3,000-word
> written report, and `docs/presentation.pptx` for the accompanying slides.

## Live demo

A working Streamlit web app is included under `/app` — run it locally:

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

Type a request like *"a spacious family car under $20,000 with great fuel economy"*
and the app returns ranked recommendations with a natural-language explanation of why
each car was picked.

## How it works

1. **Data repair** — the raw scraped dataset has a documented column-shift defect in
   some rows (values landing under the wrong JSON key). Values are recovered by
   content-pattern extraction (regex on units like `cc`, `bhp`, `kmpl`) rather than by
   trusting field labels. See `notebooks/Car_Recommendation_NLP.ipynb`, Section 3–4.
2. **NLP preference parsing** — rule-based extraction of hard constraints (max budget,
   minimum seats, fuel type) from free text.
3. **Semantic embedding** — each car is converted into a natural-language profile
   sentence and embedded with Sentence-BERT (`all-MiniLM-L6-v2`); automatically falls
   back to TF-IDF if there's no internet access.
4. **Hybrid ranking** — combines semantic similarity with budget-fit and
   constraint-violation penalties into a single ranked score.
5. **Natural-language response** — the top results are turned into a short explanation
   of why each car was recommended.

## Repository structure

```
.
├── app/                    # Streamlit demo app
│   ├── app.py               # UI
│   ├── recommender.py       # Core NLP/recommendation logic (reusable, no UI dependency)
│   ├── requirements.txt
│   ├── test_app.py          # Headless smoke test (streamlit.testing.v1)
│   └── data/                 # Bundled dataset copy so the app runs standalone
├── notebooks/
│   └── Car_Recommendation_NLP.ipynb   # Full annotated pipeline, executed with outputs
├── data/
│   ├── structured_car_data_cleaned.json    # Raw dataset (see docs/DATA.md)
│   └── structured_bike_data_cleaned.json   # Companion dataset (not used; bundled as provided)
├── docs/
│   ├── DATA.md               # Data dictionary & known data-quality issues
│   ├── report.docx            # 3,000-word written report
│   └── presentation.pptx      # Slide deck
├── questionnaire/
│   └── questionnaire.md       # Survey instrument used for user-preference validation
├── results/
│   └── evaluation_results.csv # Output of the notebook's evaluation section
├── requirements.txt
├── LICENSE
└── README.md
```

## Dataset

**Comprehensive Vehicle Specifications Dataset** (Kaggle, Adarsh, 2025):
https://www.kaggle.com/datasets/adarsh1077/comprehensive-vehicle-specifications-dataset

504 real car listings scraped from Indian automotive portals. See `docs/DATA.md` for
the full data dictionary, cleaning steps, and a documented data-quality defect (and its
fix) discovered during this project.

## Setup

```bash
pip install -r requirements.txt
```

Then either open `notebooks/Car_Recommendation_NLP.ipynb` in Jupyter/Google Colab, or
run the Streamlit app as shown above.

## Related work / references

See `docs/report.docx` for the full literature review and reference list (managed in
Mendeley; see `docs/references.bib` for the importable citation file). Key related
repositories consulted during this project:

- https://www.kaggle.com/code/abdelrahmanahmed110/cars-recommendation-system
- https://github.com/UKPLab/sentence-transformers (Sentence-BERT reference implementation)

## Author

_(add your name, student ID, course, and institution)_

## License

MIT — see `LICENSE`.
