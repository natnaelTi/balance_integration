import frappe
from frappe import _
from balance_integration.utils import get_balance_settings
from balance_integration.api.transactions import (
    create_balance_transaction,
    confirm_transaction,
    capture_transaction
)
from balance_integration.api.credit_notes import create_balance_credit_note

def handle_sales_invoice_submit(doc, method):
    """Handle Sales Invoice submission by creating and capturing Balance transaction"""
    try:
        # Get Balance settings first
        settings = get_balance_settings()
        
        # Ensure we have a proper document
        # if not doc:
        #     frappe.throw(_("No document provided"))
        
        # Basic validation
        if not doc.doctype == "Sales Invoice":
            frappe.throw(_("Invalid document type"))
        
        # Create transaction
        transaction = create_balance_transaction(doc, settings)
        
        # Confirm transaction
        confirm_transaction(transaction['id'], settings)
        
        # Capture transaction
        capture_transaction(transaction['id'], settings)
        
        # Store Balance transaction ID in custom field
        frappe.db.set_value('Sales Invoice', doc.name, 'balance_transaction_id', 
                           transaction['id'], update_modified=False)
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(str(e), "Balance Payment Processing Error")
        frappe.throw(_("Error processing Balance payment. Please check error logs."))

def handle_credit_note_submit(doc, method):
    """Handle Credit Note submission by creating Balance credit note"""
    try:
        settings = get_balance_settings()
        create_balance_credit_note(doc, settings)
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Credit Note Processing")
        frappe.throw(_("Error processing Balance credit note. Please check error logs."))