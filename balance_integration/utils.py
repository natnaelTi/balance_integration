import frappe
from frappe import _
import requests

def get_balance_settings():
    """Get Balance API settings"""
    settings = frappe.get_single("Balance Settings")
    
    if not settings.api_key or not settings.api_base_url:
        frappe.throw(_("Please configure Balance Settings"))
    
    return settings

def get_customer_information(customer_name):
    """Get customer information from Customer doctype"""
    if not customer_name:
        frappe.throw(_("Customer name is required"))
        
    customer = frappe.get_doc("Customer", customer_name)
    if not customer:
        frappe.throw(_("Customer not found"))
    
    if not customer.email_id:
        frappe.throw(_("Customer email is required"))
        
    if not customer.mobile_no:
        frappe.throw(_("Customer mobile number is required"))
    
    return {
        "email": customer.email_id,
        "mobile_no": customer.mobile_no,
        "customer_name": customer.customer_name
    }

def get_shipping_address(shipping_address_name):
    """Get shipping address information"""
    if not shipping_address_name:
        frappe.throw(_("Shipping address name is required"))
        
    shipping_address = frappe.get_doc("Address", shipping_address_name)
    if not shipping_address:
        frappe.throw(_("Shipping Address not found"))
        
    country = frappe.get_doc("Country", shipping_address.country)
    if not country or not country.code:
        frappe.throw(_("Invalid country code in shipping address"))
    
    return {
        "addressLine1": shipping_address.address_line1 or "",
        "addressLine2": shipping_address.address_line2 or "",
        "zipCode": shipping_address.pincode or "",
        "city": shipping_address.city or "",
        "state": shipping_address.state or "",
        "countryCode": country.code
    }

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