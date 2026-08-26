# Questionnaire: AI-Powered Car Recommendation System (NLP)

**Purpose:** to understand how people currently choose cars, which factors matter most
to them, and to gather early user feedback on a natural-language car recommendation
prototype. Responses inform both the system's design (which preferences the NLP parser
should prioritize) and its evaluation (whether recommendations feel relevant).

**Estimated time:** 3–5 minutes. Anonymous. No personally identifying information is
collected beyond broad demographic categories.

---

### Section A — About You

1. What is your age group?
   - Under 18 / 18–24 / 25–34 / 35–44 / 45–54 / 55+

2. Do you currently own a car, or are you planning to buy one?
   - I own a car / I'm actively looking to buy / I'm considering buying in the future / Neither

3. How would you rate your knowledge of car specifications (engine size, horsepower, etc.)?
   - (1) Not knowledgeable at all — (5) Very knowledgeable *(5-point scale)*

### Section B — Car-Buying Preferences

4. When choosing a car, how important is each of the following? *(1 = Not important, 5 = Extremely important)*
   - Budget / price
   - Fuel efficiency
   - Performance (horsepower, acceleration)
   - Safety rating
   - Seating capacity / space
   - Brand reputation
   - Fuel type (Petrol/Diesel/Hybrid/Electric)

5. What is your typical budget range for a car? *(select currency-appropriate range or leave as-is)*
   - Under $10,000 / $10,000–$20,000 / $20,000–$40,000 / $40,000–$80,000 / Over $80,000

6. What do you primarily use (or would use) a car for?
   - Daily commuting / Family use / Long road trips / Business/professional / Off-road / Other (please specify)

7. How do you currently research or decide which car to buy? *(select all that apply)*
   - Manufacturer websites / Comparison sites / Friends & family recommendations / Online reviews / Dealership visits / Social media / Other

8. Have you ever used an online car recommendation tool or configurator?
   - Yes / No
   - If yes, how satisfied were you with it? *(1–5 scale, or N/A)*

### Section C — Natural-Language Interaction

9. If you could describe your ideal car in a sentence (instead of filling out filters/dropdowns), would you prefer that?
   - Yes, definitely / Probably / Not sure / Probably not / No, I prefer filters

10. Try describing your ideal car in one sentence (e.g. *"a fuel-efficient family car under $20,000 with good safety"*):
    - *(open text)*

11. What would make you trust an AI-generated car recommendation? *(select all that apply)*
    - Clear explanation of why it was recommended / Ability to see the underlying specs / Reviews from other users / Comparison with alternatives / Nothing — I wouldn't trust it / Other

### Section D — Prototype Feedback *(only if the respondent has tried the demo app)*

12. Did the recommendation results match what you asked for?
    - Very well / Somewhat / Not really / I didn't try it

13. Was the explanation for each recommendation clear and useful?
    - (1) Not useful — (5) Very useful

14. What's one thing that could be improved about the recommendations or the explanation?
    - *(open text)*

15. Any other comments or suggestions?
    - *(open text)*

---

## Deployment instructions (for the required screenshot)

1. Go to **forms.google.com** → **Blank form**.
2. Title it *"AI-Powered Car Recommendation System — User Survey"*.
3. Add each question above using the matching Google Forms question type:
   - Age group, budget range, usage, deployment questions → **Multiple choice**
   - "Select all that apply" questions → **Checkboxes**
   - 1–5 importance/satisfaction questions → **Linear scale**
   - Open-ended questions (10, 14, 15) → **Paragraph**
4. Click **Send** → copy the shareable link, distribute to a small sample (classmates,
   friends, family — aim for at least 10–15 responses for a meaningful summary).
5. Once you have a few responses, open the **Responses** tab, and take a screenshot of
   both (a) the form itself and (b) the responses summary — insert both into the
   report's **Appendix** (Activity 5.1) as required.
6. Optionally summarize response patterns (e.g. "80% of respondents ranked budget as
   the most important factor") in the report's **Results** section to support your
   design choices (e.g. why budget is a hard constraint in the NLP parser, while body
   type is not).
