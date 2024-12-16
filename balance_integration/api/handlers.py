import frappe
from frappe import _
from balance_integration.utils import (
    get_balance_settings,
    update_customer_data
)
from balance_integration.api.transactions import (
    create_balance_transaction,
    confirm_transaction,
    capture_transaction
)
from balance_integration.api.credit_notes import create_balance_credit_note

def process_balance_transaction(doc, method):
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

        buyer_id = transaction.get('buyerId')
        if not buyer_id:
            frappe.throw(_("No buyer ID in Balance response"))
            
        update_result = update_customer_data(doc.customer, buyer_id)

        # Confirm transaction
        confirm_result = confirm_transaction(transaction_id, buyer_id, settings)
        if not confirm_result:
            frappe.throw(_("Failed to confirm transaction"))
        
        # Capture transaction
        capture_result = capture_transaction(transaction_id, settings)
        if not capture_result:
            frappe.throw(_("Failed to capture transaction"))

        invoice_id = capture_result.get('invoices')
        if not invoice_id:
            frappe.throw(_("No invoice ID in Balance response"))

        # Store Balance transaction ID in custom field
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_balance_transaction_id', 
                           transaction_id, update_modified=False)
        frappe.db.commit()

        #Store Balance invoice ID in custom field
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_balance_invoice_id', 
                           invoice_id[0], update_modified=False)
        frappe.db.commit()
        
        frappe.msgprint(_("Balance payment processed successfully"))
        
    except Exception as e:
        # Limit error message length for logging
        short_error = str(e)[:140] if len(str(e)) > 140 else str(e)
        frappe.log_error(short_error, "Balance Payment Error")
        frappe.throw(_("Error processing Balance payment: {0}").format(short_error))

def process_balance_credit_note(doc, method):
    """Handle Credit Note submission by creating Balance credit note"""
    try:
        settings = get_balance_settings()
        if not settings:
            frappe.throw(_("Balance Settings not configured"))
        
        invoice = frappe.get_doc('Sales Invoice', doc.name)
        if not invoice:
            frappe.throw(_("Sales Invoice not found"))
        
        credit_note = create_balance_credit_note(doc, settings)
        # Validate credit note response
        if not credit_note:
            frappe.throw(_("No response from Balance API"))
        
        credit_note_id = credit_note.get('id')
        #Store Balance credit note ID in custom field
        frappe.db.set_value('Sales Invoice', doc.name, 'custom_balance_credit_note_id', 
                           credit_note_id, update_modified=False)
        frappe.db.commit()
        
        frappe.msgprint(_("Balance credit note processed successfully"))
    except Exception as e:
        frappe.log_error(f"Balance Integration Error: {str(e)}", "Balance Credit Note Processing")
        frappe.throw(_("Error processing Balance credit note. Please check error logs."))

def handle_sales_invoice_submit(doc, method):
    if doc.is_return:
        process_balance_credit_note(doc, method)

    if not doc.is_return:
        process_balance_transaction(doc, method)
