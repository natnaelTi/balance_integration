import frappe
from frappe import _
from balance_integration.utils import get_balance_settings, make_request

def create_balance_credit_note(doc, settings):
    """Create a credit note in Balance"""
    endpoint = f"{settings.api_base_url}/credit-notes"
    
    payload = {
        "amount": doc.grand_total,
        "currency": doc.currency,
        "reference": doc.name,
        "customer": {
            "email": doc.customer_email,
            "name": doc.customer_name
        }
    }
    
    return make_request("POST", endpoint, settings.api_key, payload)