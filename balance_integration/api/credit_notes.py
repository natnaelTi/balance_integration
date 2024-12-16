import frappe
from frappe import _
from balance_integration.utils import get_balance_settings, make_request

def create_balance_credit_note(doc, settings):
    """Create a credit note in Balance"""
    endpoint = f"{settings.api_base_url}/credit-notes"
    
    payload = {
        "invoiceId": doc.custom_balance_invoice_id,
        "lines": [{
            "amount": doc.grand_total,
            "reason": f"Returning against invoice: {doc.return_against} for {doc.remarks}"
        }]
    }
    
    try:
        result = make_request("POST", endpoint, settings.api_key, payload)
        if result and result.get('id'):
            return result
        else:
            frappe.throw(_("Failed to create credit note in Balance"))

    except Exception as e:
        frappe.throw(_("Error creating credit note: {0}").format(str(e)[:140]))