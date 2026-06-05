"""
LLM Support Layer for Clinical Input Assistant.
Provides optional free LLM integration using the Gemini API endpoint.
"""
import requests
import json

def get_llm_explanation(query: str, context: str = "", api_key: str = None) -> str:
    """
    Calls the free Gemini 1.5 Flash API to get educational explanations.
    Returns the markdown string from the LLM, or None if the layer is not active/fails.
    """
    if not api_key or not api_key.strip():
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "You are a Clinical Input Assistant for the ClinicalAI Decision Support System. "
        "Your task is to provide medical education, explain predictor fields, assist with system navigation, "
        "or explain diagnostic risk reports based on the context provided. "
        "CRITICAL: Never invent diagnostic/ECG measurements, write diagnoses, or prescribe treatments. "
        "Keep your response educational, extremely professional, concise (under 150 words), and formatted in clean markdown.\n\n"
    )
    if context:
        prompt += f"Context:\n{context}\n\n"
    prompt += f"User Inquiry:\n{query}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=8)
        if response.status_code == 200:
            res_data = response.json()
            # Extract text from the candidate structure
            text = res_data['candidates'][0]['content']['parts'][0]['text']
            return text.strip()
        else:
            # Silently log and fall back to local rule-based engine
            print(f"[LLM LOG] Gemini API returned status code {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[LLM LOG] Gemini API call failed: {e}")
        
    return None
