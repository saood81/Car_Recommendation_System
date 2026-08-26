import sys
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=120)
at.run()

print("Initial run exceptions:", at.exception)
assert not at.exception, f"App crashed on initial load: {at.exception}"

# Type a query and click "Get Recommendations"
at.text_input[0].set_value("fuel-efficient family car under $15,000 with good safety")
at.button[0].click()  # "Get Recommendations" (main-content button renders first)
at.run()

print("Post-query exceptions:", at.exception)
assert not at.exception, f"App crashed after query: {at.exception}"

# Check the AI response text and dataframe rendered
markdowns = [m.value for m in at.markdown]
found_response = any("Recommended because" in m or "AI response" in m for m in markdowns) or len(at.dataframe) > 0
print("Found dataframe outputs:", len(at.dataframe))
print("Found metric outputs:", len(at.metric))
for met in at.metric:
    print("  metric:", met.label, "=", met.value)

assert len(at.dataframe) > 0, "No results dataframe rendered"
print("\nSMOKE TEST PASSED")
