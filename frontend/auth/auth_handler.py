import requests
import streamlit as st
import time

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

def authenticate(username, password, role):
    """
    Handles the authentication logic by communicating with the backend API.
    Includes a fallback for demo credentials.
    """
    success = False
    token = None
    display_name = username

    try:
        # Actual API call
        res = requests.post(
            f"{API_URL}/login", 
            data={"username": username, "password": password},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            token = data.get("access_token")
            # Override display name if backend provides a full_name
            backend_full_name = data.get("full_name")
            if backend_full_name:
                display_name = backend_full_name
            success = True
        else:
            # Only log mismatch if it's not the demo account
            if not (username == "admin" and password == "password"):
                st.sidebar.error(f"Login failed: {res.status_code}")
    except requests.exceptions.ConnectionError:
        # Silently log to audit, but don't block demo fallback
        st.session_state.audit_logs.append(f"Backend offline at {time.ctime()}")
        if not (username == "admin" and password == "password"):
            st.toast("⚠️  Backend API is currently offline. Using offline mode.", icon="📡")
    except Exception as e:
        st.session_state.audit_logs.append(f"Auth error at {time.ctime()}: {str(e)}")

    # Demo Fallback
    if not success:
        if username == "admin" and password == "password":
            token = "demo_jwt_token_256bit"
            display_name = "Dr. Admin" if role == "doctor" else "Patient Admin"
            success = True
    
    return success, token, display_name


def verify_session():
    """
    Verifies if the current JWT token is still valid.
    In a real app, this would check with the backend.
    """
    if not st.session_state.get("token"):
        return False

    # Simple check for now as per existing logic
    return True


def register_patient(full_name: str, email: str, password: str):
    """
    Patient account registration.
    Calls backend POST /register endpoint.
    Returns: (success: bool, message: str)
    """
    try:
        res = requests.post(f"{API_URL}/register",
            json={
                "username": email, # email as username for patients
                "email": email, 
                "password": password,
                "role": "patient",
                "full_name": full_name,
                "hospital_name": ""
            },
            timeout=5)
        
        if res.status_code == 200:
            st.session_state.audit_logs.append(
                f"Patient registration success: {email} at {time.ctime()}"
            )
            return True, "Account created successfully"
            
        try:
            return False, res.json().get("detail", "Registration failed")
        except Exception:
            return False, f"Registration error (HTTP {res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def register_doctor(clinical_id: str, hospital_name: str, doctor_name: str, email: str, password: str):
    """
    Doctor account registration.
    Calls backend POST /register endpoint.
    Returns: (success: bool, message: str)
    """
    try:
        res = requests.post(f"{API_URL}/register",
            json={
                "username": clinical_id,
                "email": email, 
                "password": password,
                "role": "doctor",
                "full_name": doctor_name,
                "hospital_name": hospital_name
            },
            timeout=5)
        
        if res.status_code == 200:
            st.session_state.audit_logs.append(
                f"Doctor registration success: {clinical_id} at {time.ctime()}"
            )
            return True, "Account created successfully"
            
        try:
            return False, res.json().get("detail", "Registration failed")
        except Exception:
            return False, f"Registration error (HTTP {res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Registration error: {str(e)}"
