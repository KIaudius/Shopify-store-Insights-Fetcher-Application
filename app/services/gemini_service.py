# app/services/gemini_service.py

import os
import json
import time
from typing import List, Dict, Any
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        # Initialize the Gen AI client
        self.client = genai.Client(api_key=api_key)

    def _call_gemini(self, prompt: str, json_output: bool = True):
        max_retries = 5
        base_delay = 2  # seconds
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                if not json_output:
                    return response.text.strip()
                
                # Clean the response text to ensure it's valid JSON
                text_response = response.text.strip()
                if text_response.startswith('```json'):
                    text_response = text_response[7:-3].strip()
                elif text_response.startswith('```'):
                    text_response = text_response[3:-3].strip()

                return json.loads(text_response)

            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                elif isinstance(e, json.JSONDecodeError):
                    print(f"Error decoding JSON from Gemini: {e}")
                    # print(f"Raw response was: {response.text}") # response might not be defined
                    return {} if json_output else ""
                else:
                    print(f"An error occurred calling Gemini API on attempt {attempt + 1}: {e}")
                    break # Break on other errors

        # Return default value if all retries fail
        print("All retries failed for Gemini API call.")
        return {} if json_output else ""

    def extract_brand_context(self, html_content: str, store_url: str) -> Dict[str, Any]:
        prompt = f"""
Analyze the following HTML content from a Shopify store ({store_url}) and extract brand context information.

Please extract and structure the following information in JSON format:
{{
    "store_name": "Brand/Store name",
    "brand_description": "Brief description of the brand",
    "about_us": "About us section content",
    "mission_statement": "Mission or vision statement",
    "founded_year": "Year founded (if mentioned)",
    "headquarters": "Location/headquarters (if mentioned)"
}}

HTML Content (first 5000 characters):
{html_content[:5000]}

Return only valid JSON.
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, dict) else {}

    def extract_faqs(self, html_content: str) -> List[Dict[str, str]]:
        prompt = f"""
Analyze the following HTML and extract all FAQ entries.

Return a JSON array of objects:
[{{"question":"…","answer":"…","category":"…"}}]

HTML Content (first 8000 chars):
{html_content[:8000]}

Return only JSON array (or [] if none).
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, list) else []

    def extract_contact_info(self, html_content: str) -> Dict[str, Any]:
        prompt = f"""
Extract contact information from this HTML. Return JSON:
{{"email":"…","phone":"…","address":"…","support_hours":"…"}}

HTML Content (first 5000 chars):
{html_content[:5000]}

Return only JSON.
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, dict) else {}

    def extract_social_handles(self, html_content: str) -> List[Dict[str, str]]:
        prompt = f"""
Extract social media handles from this HTML. Return a JSON array:
[{{"platform":"…","url":"…","handle":"…"}}]

HTML Content (first 5000 chars):
{html_content[:5000]}

Return only JSON array (or []).
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, list) else []

    def find_competitors(self, brand_name: str, industry: str = "") -> List[str]:
        prompt = f"""
Find 3–5 main competitors for the brand "{brand_name}"{f" in the {industry} industry" if industry else ""}. 
Return a JSON array of URLs:
["https://competitor1.com", ...]
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, list) else []

    def analyze_competitors(self, main_brand: Dict, competitors: List[Dict]) -> Dict[str, Any]:
        prompt = f"""
Analyze this competitive landscape.

Main Brand: {json.dumps(main_brand)[:2000]}
Competitors: {json.dumps(competitors)[:2000]}

Return JSON:
{{"analysis_summary":"…","competitive_advantages":["…"],"market_insights":["…"]}}
        """
        result = self._call_gemini(prompt)
        return result if isinstance(result, dict) else {{
            "analysis_summary": "Analysis failed",
            "competitive_advantages": [],
            "market_insights": []
        }}
