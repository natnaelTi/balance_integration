import frappe
from frappe import _
import requests

def get_balance_settings():
    """Get Balance API settings"""
    settings = frappe.get_single("Balance Settings")
    
    if not settings:
        frappe.throw(_("Balance Settings not found"))
    
    if not settings.api_key:
        frappe.throw(_("Balance API Key is required"))
        
    if not settings.api_base_url:
        frappe.throw(_("Balance API Base URL is required"))
    
    # Log settings (minimal)
    # frappe.log_error(f"Using Balance API: {settings.api_base_url}")
    
    return settings

def make_request(method, endpoint, api_key, data=None):
    """Make API request to Balance"""
    # Ensure API key is properly formatted
    # if not api_key.startswith('sk_'):
    #     api_key = f"sk_sandbox_{api_key}"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        # Log minimal request info
        # frappe.log_error(f"Balance API Request: {method} {endpoint}")
        
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=data
        )
        
        # Get response text for error handling
        # try:
        response_data = response.json()
        # except:
        #     response_data = response.text[:100]  # Limit text length
        
        # Log minimal response info
        frappe.log_error(f"Balance API Status: {response.status_code}")
        
        if response.status_code == 401:
            frappe.log_error(f"Auth Error Response: {response_data}")
            frappe.throw(_("Authentication failed. Please check your API key."))
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {str(e)}"  # Limit error message length
        frappe.log_error(error_msg)
        raise