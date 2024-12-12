import frappe
from frappe import _
import requests

def get_balance_settings():
    """Get Balance API settings"""
    settings = frappe.get_single("Balance Settings")
    
    if not settings.api_key or not settings.api_base_url:
        frappe.throw(_("Please configure Balance Settings"))
    
    return settings

def make_request(method, endpoint, api_key, data=None):
    """Make API request to Balance"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Balance API Error: {str(e)}", "Balance API Request")
        raise