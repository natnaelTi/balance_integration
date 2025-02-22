import frappe
from frappe import _
from balance_integration.utils import get_balance_settings, make_request

@frappe.whitelist()
def send_qualification_link(customer):
    """Send qualification link to customer"""
    try:
        settings = get_balance_settings()
        customer_doc = frappe.get_doc("Customer", customer)
        
        endpoint = f"{settings.api_base_url}/buyers/{customer_doc.custom_balance_buyer_id}/qualification"
        
        return make_request("POST", endpoint, settings.api_key)
        
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Qualification Link")
        frappe.throw(_("Error sending qualification link. Please check error logs."))