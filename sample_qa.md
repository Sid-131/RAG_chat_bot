# Sample QA Context Evaluation

This document demonstrates the output format expected from the fully deployed RAG Chatbot.

It validates the three core rules instructed during Phase 7 and Phase 8:
1.  **Factual answers are $\le$ 3 sentences.**
2.  **Exactly 1 source citation link is provided.**
3.  **Advisory queries are recognized by the Guardrails and politely refused with educational links.**

---

### **Test Case 1: Factual Retrieval (Success)**

**USER QUERY:**
> What is the exit load for Mirae Asset ELSS Tax Saver Fund?

**CHATBOT RESPONSE:**
> The exit load for Mirae Asset ELSS Tax Saver Fund is Nil. Please note that this fund has a statutory lock-in period of 3 years from the date of allotment, during which units cannot be redeemed or switched out.
>
> [Source](https://www.miraeassetmf.co.in/schemes/elss-tax-saver)

---

### **Test Case 2: Out of Domain / Insufficient Context (Fallback)**

**USER QUERY:**
> Does the HDFC Bank stock pay a good dividend tonight?

**CHATBOT RESPONSE:**
> The information is not available in the provided official sources.

---

### **Test Case 3: Advisory Guardrail Trigger (Refusal)**

**USER QUERY:**
> Which mutual fund is the best one for me to invest my bonus in?

**CHATBOT RESPONSE:**
> I can only provide factual information about mutual funds. I cannot give investment advice. For personalised guidance or portfolio building, please refer to educational resources from:
> 
> - [SEBI Investor Website](https://investor.sebi.gov.in/)
> - [AMFI Investor Corner](https://www.amfiindia.com/investor-corner)
> - [Groww Help Center](https://groww.in/help)
