# Data Documentation

## Source

**Comprehensive Vehicle Specifications Dataset**, Adarsh (2025), Kaggle.
https://www.kaggle.com/datasets/adarsh1077/comprehensive-vehicle-specifications-dataset

Scraped from leading Indian automotive listing portals. Distributed as two JSON files:
`structured_car_data_cleaned.json` (504 records, used in this project) and
`structured_bike_data_cleaned.json` (motorcycles, not used).

## Raw schema

Each record is a flat JSON object with these keys (all optional except `name`):

| Key | Expected content |
|---|---|
| `name` | Full model name, e.g. `"Maruti Suzuki Ertiga"` |
| `price` | Price range string, e.g. `"Rs.8.84 - 13.13 Lakh* (View On Road Price)"` |
| `fuel` | Fuel type, e.g. `"Petrol/CNG"` |
| `mileage` | Fuel efficiency, e.g. `"20.51 kmpl"` |
| `transmission` | e.g. `"Manual/Automatic"` |
| `cc` | Engine displacement, e.g. `"1462 cc"` |
| `power` | Engine power, e.g. `"101.64 bhp"` |
| `safety` | Star rating or seat count, e.g. `"4 Star Safety"` or `"5 Seats"` |
| `seats` | Seat count (rarely populated) |
| `type` | Always `"car"` for this file |

## Known data-quality issue: column-shifted rows

**Discovered during this project.** A subset of rows have values shifted into the
wrong key — a classic artifact of a scraper assuming a fixed column count per listing
page, where a missing field silently shifts every subsequent value one position to the
left. Example (Aston Martin Vantage, verbatim from the source file):

```json
{
  "name": "Aston Martin Vantage",
  "price": "Rs.3.99 Cr* (View On Road Price)",
  "fuel": "7 kmpl",            // actually the mileage value
  "mileage": "3998 cc",        // actually the engine displacement
  "transmission": "656 bhp",   // actually the engine power
  "cc": "2 Seats",             // actually the seat count
  "power": null, "safety": null, "seats": null
}
```

**Fix applied** (see `app/recommender.py::parse_record` and the notebook, Section 4):
every value is extracted by **content pattern** (regex matched against the unit or
keyword — `cc`, `bhp`, `kmpl`, `Star Safety`, `Seats`, `Rs. ... Lakh/Cr`) from the
concatenation of *all* fields in a row, rather than trusted by key. This recovers the
correct value regardless of which key it was filed under.

## Cleaned schema (after `load_and_clean()`)

| Column | Type | Notes |
|---|---|---|
| `make` | str | Brand, handles known multi-word brands (e.g. "Maruti Suzuki") |
| `model` | str | Remainder of the name after the brand |
| `price_usd` | float | Converted from INR (Lakh/Crore) at an approximate fixed rate of 1 USD ≈ 83 INR. Rows with no recoverable price are dropped. |
| `engine_cc` | int | Engine displacement. Missing values imputed with the dataset median. |
| `engine_power_hp` | float | Engine power (bhp, treated as ≈ hp). Missing values imputed with the dataset median. |
| `mileage_kmpl` | float | Fuel efficiency. Missing values imputed with the dataset median. |
| `fuel_type` | str | One of Petrol / Diesel / CNG / Hybrid / Electric / LPG / `"Unknown"`. Primary fuel taken as the **leftmost-occurring** keyword in the record (so "Petrol/CNG" → Petrol, not CNG). Not imputed — left as `"Unknown"` when absent. |
| `transmission` | str | Manual / Automatic / CVT / AMT / DCT / `"Unknown"`. Not imputed. |
| `safety_rating` | int (1–5) | Star rating. Missing values imputed with the dataset median, rounded. |
| `seats` | int (2–9) | Missing values imputed with the dataset median, rounded. |
| `car_profile` | str | Auto-generated natural-language description used for embedding. |

## Completeness after extraction (before imputation)

| Field | % non-null (of 504) |
|---|---|
| price | 99.6% |
| engine_cc | 71.8% |
| engine_power_hp | 57.9% |
| mileage_kmpl | 68.3% |
| fuel_type | 66.5% |
| transmission | 35.5% |
| safety_rating | 22.2% |
| seats | 57.7% |

## Limitations

- **No body-type/segment field** (SUV, sedan, hatchback, etc.) exists in the source
  data, so usage-based filtering relies only on semantic similarity of the free-text
  query against the generated profile, not a hard constraint.
- **Median imputation** for missing numeric fields is a simplification — it does not
  account for make/segment differences, and creates ties between dissimilar cars that
  happen to share an imputed value.
- **Currency conversion** uses one fixed approximate exchange rate rather than live
  rates.
- **Two rows dropped** (of 504) due to unrecoverable price information.
