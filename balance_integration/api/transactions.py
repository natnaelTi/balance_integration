import frappe
from frappe import _
from balance_integration.utils import make_request

"""Create a transaction in Balance"""
def create_balance_transaction(doc, settings):
    # Basic validation
    if not doc:
        frappe.throw(_("No document provided"))
        
    if not doc.doctype == "Sales Invoice":
        frappe.throw(_("Invalid document type"))
        
    if not doc.items:
        frappe.throw(_("Sales Invoice must have at least one item"))

    try:
        # Get customer information
        customer = frappe.get_doc("Customer", doc.customer)
        if not customer:
            frappe.throw(_("Customer not found"))
            
        if not customer.email_id:
            frappe.throw(_("Customer email is required"))
            
        if not customer.mobile_no:
            frappe.throw(_("Customer mobile number is required"))
            
        # Get shipping address
        if not doc.shipping_address_name:
            frappe.throw(_("Shipping address is required"))
            
        shipping_address = frappe.get_doc("Address", doc.shipping_address_name)
        if not shipping_address:
            frappe.throw(_("Shipping address not found"))
            
        country = frappe.get_doc("Country", shipping_address.country)
        if not country or not country.code:
            frappe.throw(_("Invalid country code in shipping address"))

        # Create line items
        lines = []
        for item in doc.items:
            if not item.qty or not item.rate:
                frappe.throw(_("Item quantity and rate are required"))
                
            line_item = {
                "title": item.item_name or item.item_code,
                "quantity": float(item.qty),
                "price": float(item.rate)
            }
            lines.append(line_item)

        if doc.total_taxes_and_charges:
            lines.append({
                "tax": float(doc.total_taxes_and_charges)
            })

        # Create payload
        payload = {
            "communicationConfig": {
                "emailsTo": [customer.email_id]  # Use customer email instead of owner
            },
            "amount": float(doc.grand_total),
            "currency": doc.currency,
            "buyer": {
                "employee": {
                    "email": doc.modified_by
                },
                "email": customer.email_id,
                "first_name": customer.customer_name,
                "phone": customer.mobile_no,
                "draft": False,
            },
            "plan": { 
                "planType": "invoice"
            },
            "lines": lines,
            "externalReferenceId": doc.name,
            "shippingAddress": {
                "addressLine1": shipping_address.address_line1 or "",
                "addressLine2": shipping_address.address_line2 or "",
                "zipCode": shipping_address.pincode or "",
                "city": shipping_address.city or "",
                "state": shipping_address.state or "",
                "countryCode": country.code or ""
            },
            "totalDiscount": float(doc.discount_amount or 0),
            "marketplaceFixedTake": 0,
            "autoPayouts": False,
            "statementDescriptor": {
                "charge": "Balance Invoice Processed via ERPNext"
            }
        }
        
        # Make API request
        endpoint = f"{settings.api_base_url}/transactions"
        return make_request("POST", endpoint, settings.api_key, payload)
        
    except Exception as e:
        frappe.log_error(f"Error creating Balance transaction: {str(e)}")
        raise

def confirm_transaction(transaction_id, settings):
    """Confirm a Balance transaction"""
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/confirm"
    return make_request("POST", endpoint, settings.api_key)

def capture_transaction(transaction_id, settings):
    """Capture a Balance transaction"""
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/capture"
    return make_request("POST", endpoint, settings.api_key)