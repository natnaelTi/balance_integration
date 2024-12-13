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
        if not settings:
            frappe.throw(_("Balance Settings not configured"))
        
        invoice = frappe.get_doc('Sales Invoice', doc.name)
        if not invoice:
            frappe.throw(_("Sales Invoice not found"))
        
        # Create transaction
        transaction = create_balance_transaction(invoice, settings)
        
        # Validate transaction response
        if not transaction:
            frappe.throw(_("No response from Balance API"))
            
        transaction_id = transaction.get('id')
        if not transaction_id:
            frappe.throw(_("No transaction ID in Balance response"))
            
        frappe.log_error(f"Created Balance transaction: {transaction_id}")
        
        # Confirm transaction
        confirm_result = confirm_transaction(transaction_id, settings)
        frappe.log_error(f"Confirmed transaction: {transaction_id}")
        
        # Capture transaction
        capture_result = capture_transaction(transaction_id, settings)
        frappe.log_error(f"Captured transaction: {transaction_id}")
        
        # Store Balance transaction ID in custom field
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_balance_transaction_id', 
                           transaction_id, update_modified=False)
        frappe.db.commit()
        
        frappe.msgprint(_("Balance payment processed successfully"))
        
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