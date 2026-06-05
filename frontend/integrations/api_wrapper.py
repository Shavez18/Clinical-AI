import requests
import streamlit as st

def fetch_drug_interactions(api_url, headers, drug_list):
    """Fetches drug interaction data from the backend API."""
    try:
        res = requests.post(
            f"{api_url}/check/drug-interaction",
            json={"drugs": drug_list},
            headers=headers
        )
        if res.ok:
            return res.json()
        return {"error": f"API returned status {res.status_code}"}
    except Exception as e:
        return {"error": str(e)}
