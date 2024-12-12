import frappe
from frappe import _
import requests
import json
from balance_integration.utils import get_balance_settings

def handle_sales_invoice_submit(doc, method):
    """Handle Sales Invoice submission by creating and capturing Balance transaction"""
    try:
        settings = get_balance_settings()
        
        # Create transaction
        transaction = create_balance_transaction(doc, settings)
        
        # Confirm transaction
        confirm_transaction(transaction['id'], settings)
        
        # Capture transaction
        capture_transaction(transaction['id'], settings)
        
        # Store Balance transaction ID in custom field
        doc.db_set('balance_transaction_id', transaction['id'])
        
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Payment Processing")
        frappe.throw(_("Error processing Balance payment. Please check error logs."))

def handle_credit_note_submit(doc, method):
    """Handle Credit Note submission by creating Balance credit note"""
    try:
        settings = get_balance_settings()
        create_balance_credit_note(doc, settings)
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Credit Note Processing")
        frappe.throw(_("Error processing Balance credit note. Please check error logs."))

def create_balance_transaction(doc, settings):
    """Create a transaction in Balance"""
    endpoint = f"{settings.api_base_url}/transactions"
    
    payload = {
        "amount": doc.grand_total,
        "currency": doc.currency,
        "reference": doc.name,
        "customer": {
            "email": doc.customer_email,
            "name": doc.customer_name
        }
    }
    
    response = make_request("POST", endpoint, settings.api_key, payload)
    return response

def confirm_transaction(transaction_id, settings):
    """Confirm a Balance transaction"""
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/confirm"
    return make_request("POST", endpoint, settings.api_key)

def capture_transaction(transaction_id, settings):
    """Capture a Balance transaction"""
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/capture"
    return make_request("POST", endpoint, settings.api_key)

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

@frappe.whitelist()
def send_qualification_link(customer):
    """Send qualification link to customer"""
    try:
        settings = get_balance_settings()
        customer_doc = frappe.get_doc("Customer", customer)
        
        endpoint = f"{settings.api_base_url}/qualification-links"
        payload = {
            "customer": {
                "email": customer_doc.email_id,
                "name": customer_doc.customer_name
            }
        }
        
        response = make_request("POST", endpoint, settings.api_key, payload)
        return response
        
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Qualification Link")
        frappe.throw(_("Error sending qualification link. Please check error logs."))