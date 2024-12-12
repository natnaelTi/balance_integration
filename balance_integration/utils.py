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
    
    # Ensure API base URL ends with /
    # if not settings.api_base_url.endswith('/'):
    #     settings.api_base_url = f"{settings.api_base_url}/"
    
    # Log settings (minimal)
    frappe.log_error(f"Using Balance API: {settings.api_base_url}")
    
    return settings

def make_request(method, endpoint, api_key, data=None):
    """Make API request to Balance"""
    headers = {
        "x-api-key": api_key
    }
    
    try:
        frappe.log_error(
            f"Making Balance API request:\n"
            f"Method: {method}\n"
            f"Endpoint: {endpoint}\n"
            # f"Headers: {{'Content-Type': {headers['Content-Type']}, 'Accept': {headers['Accept']}}}"
        )
        
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=data
        )
        
        frappe.log_error(
            f"Balance API response:\n"
            f"Status Code: {response.status_code}\n"
            f"Response Headers: {dict(response.headers)}"
        )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = (
            f"Balance API Error:\n"
            f"Status Code: {getattr(e.response, 'status_code', 'N/A')}\n"
            f"Error Message: {str(e)}\n"
            f"Response Text: {getattr(e.response, 'text', 'N/A')}"
        )
        frappe.log_error(error_msg, "Balance API Request Error")
        raise