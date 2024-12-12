import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Add Balance Transaction ID custom field to Sales Invoice"""
    if not frappe.db.exists('Custom Field', 'Sales Invoice-balance_transaction_id'):
        create_custom_field('Sales Invoice', {
            'fieldname': 'balance_transaction_id',
            'label': 'Balance Transaction ID',
            'fieldtype': 'Data',
            'insert_after': 'payment_schedule',
            'read_only': 1,
            'no_copy': 1,
            'print_hide': 1,
            'allow_on_submit': 1  # Allow updating after submission
        })