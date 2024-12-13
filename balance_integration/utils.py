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
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=data
        )
        
        # Handle different response codes
        if response.status_code == 401:
            frappe.throw(_("Authentication failed. Please verify your API key format and value."))
        elif response.status_code in [200, 201]:  # Success codes
            return response.json()
        else:
            response.raise_for_status()
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {str(e)}"
        frappe.log_error(error_msg)
        raise