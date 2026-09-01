import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
API_KEY = os.getenv("OPENAI_API_KEY")

BUSINESS_KNOWLEDGE = """
You are Sunil AI for Sunil RO Expert, a water-purifier sales and service business in Ghaziabad/Delhi NCR.

Business:
- Sunil RO Expert
- Phone: +91 9818876665
- WhatsApp: https://wa.me/919818876665
- Email: suniltaneja1976@gmail.com
- Website: https://tanish104.github.io/sunil-ro-expert/
- Main services: RO repair, water purifier service, filter replacement, membrane replacement,
  TDS/water-quality inspection, installation/uninstallation, maintenance, and new RO enquiries.
- Do not invent current prices, stock, exact model specifications, warranties, certifications,
  service availability, or booking confirmations.

Act as a knowledgeable, honest business consultant and service advisor.
Understand natural-language questions and remember the conversation.
For purchase questions, consider water source, known water-quality information/TDS, household size,
budget and desired features. For repair questions, discuss likely causes and safe checks, then suggest
professional inspection when appropriate.
TDS alone does not establish whether water is safe; explain this when relevant.
When a fact needs current verification, use the available web-search tool and prefer authoritative
government, standards, scientific and manufacturer sources.
"""
INSTRUCTIONS = """
Answer the customer's actual question first. Do not repeat questions already answered.
Ask only for information that is genuinely needed. Give practical, concise explanations.
When the customer is ready to buy or book service, collect the minimum useful details and provide
a clear Call/WhatsApp next step. Never claim that a booking or payment has been completed unless
a real booking system confirms it.
"""

@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "service": "Sunil AI real business agent",
        "status": "online",
        "model": MODEL
    })

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "Sunil AI real business agent",
        "status": "healthy"
    })

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    previous = data.get("previous_response_id")

    if not message:
        return jsonify({"error": "Message required"}), 400

    if not API_KEY:
        return jsonify({"error": "OPENAI_API_KEY is not configured on the server"}), 500

    try:
        client = OpenAI(api_key=API_KEY)

        args = {
            "model": MODEL,
            "instructions": BUSINESS_KNOWLEDGE + "\n\n" + INSTRUCTIONS,
            "input": message,
            "store": True,
            "tools": [{"type": "web_search"}]
        }

        if previous:
            args["previous_response_id"] = previous

        response = client.responses.create(**args)

        return jsonify({
            "reply": response.output_text,
            "response_id": response.id
        })

    except Exception as exc:
        # Return a safe diagnostic message to the browser without exposing the API key.
        return jsonify({
            "error": "OpenAI request failed",
            "detail": str(exc)[:800]
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
