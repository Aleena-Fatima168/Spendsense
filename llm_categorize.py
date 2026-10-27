import json
import time

from google import genai
from google.genai import errors

CATEGORIES = [
    "Groceries",
    "Dining",
    "Transportation",
    "Subscriptions",
    "Shopping",
    "Entertainment",
    "Other",
]

MODEL = "gemini-3.8-flash"
MAX_ATTEMPTS = 4

_client = None


def get_client():
    """Creates the Gemini client on first use and reports a missing key clearly."""
    global _client
    if _client is None:
        try:
            # Reads the key from the GEMINI_API_KEY environment variable
            _client = genai.Client()
        except ValueError:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Set it in the same terminal that runs this program."
            )
    return _client


def categorize_with_llm(descriptions: list[str]) -> dict[str, str]:
    """Takes a list of merchant names and returns {merchant: category}."""
    prompt = (
        "Categorize each merchant name into exactly one of these categories: "
        f"{', '.join(CATEGORIES)}.\n"
        "Reply with ONLY a JSON object mapping each merchant name to its category. "
        "No explanation, no extra text.\n\n"
        f"Merchants: {json.dumps(descriptions)}"
    )

    client = get_client()

    response = None
    last_error = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            break
        except errors.ClientError as e:
            if e.code != 429:
                # Invalid key, wrong model name or a bad request: retrying will not help
                raise RuntimeError(
                    f"Gemini rejected the request (error code {e.code}). "
                    f"Check that the API key is valid and that the model '{MODEL}' is available."
                ) from e
            last_error = e  # 429 means rate limited, so waiting and retrying can help
        except Exception as e:
            last_error = e  # Temporary problems such as a busy server

        print(f"Attempt {attempt + 1} of {MAX_ATTEMPTS} failed: {last_error}")
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(5 * (attempt + 1))

    if response is None:
        raise RuntimeError(
            f"Gemini did not respond after {MAX_ATTEMPTS} attempts: {last_error}"
        )

    text = (response.text or "").strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return {d: "Other" for d in descriptions}

    # Safety check: if the LLM returns an unexpected category, fall back to "Other"
    return {
        d: result.get(d, "Other") if result.get(d) in CATEGORIES else "Other"
        for d in descriptions
    }


if __name__ == "__main__":
    test_merchants = [
        "Joe's Corner Cafe",
        "Shell Gas Station",
        "Hulu",
        "Local Pharmacy",
        "Domino's Pizza",
        "Daraz Online",
    ]
    output = categorize_with_llm(test_merchants)
    for merchant, category in output.items():
        print(f"{merchant:25} -> {category}")