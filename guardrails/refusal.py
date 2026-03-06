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
        "I can only provide factual information about mutual funds. I cannot give investment advice. "
        "For personalised guidance or portfolio building, please refer to educational resources from:\n\n"
        "- [SEBI Investor Website](https://investor.sebi.gov.in/)\n"
        "- [AMFI Investor Corner](https://www.amfiindia.com/investor-corner)\n"
        "- [Groww Help Center](https://groww.in/help)"
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
