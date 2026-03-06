"""
refusal.py
----------
Pre-defined refusal response templates for different guard trigger types.

Template types:
  - ADVISORY:      Query asks for investment advice or recommendations
  - OUT_OF_DOMAIN: Query is unrelated to mutual funds on Groww
  - NO_CONTEXT:    Query is factual but no relevant chunks were found
"""

REFUSALS = {
    "ADVISORY": (
        "I'm not able to provide investment recommendations or financial advice. "
        "For personalised guidance, please consult a SEBI-registered investment advisor. "
        "I can help you with factual information about any specific mutual fund scheme."
    ),
    "OUT_OF_DOMAIN": (
        "I can only answer factual questions about mutual fund schemes on Groww, "
        "such as expense ratios, exit loads, SIP minimums, riskometer levels, and benchmark indices."
    ),
    "NO_CONTEXT": (
        "I don't have that information in my knowledge base. "
        "Please refer to the scheme's official AMC page or the Groww Help Center for accurate details."
    ),
}


def get_refusal(trigger: str) -> str:
    """
    Return the appropriate refusal message for the given trigger type.
    Falls back to OUT_OF_DOMAIN if trigger is unrecognised.
    """
    return REFUSALS.get(trigger, REFUSALS["OUT_OF_DOMAIN"])
