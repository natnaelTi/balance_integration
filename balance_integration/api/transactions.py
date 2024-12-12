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
        # Create line items
        lines = []
        for item in doc.items:
            line_item = {
                "title": item.item_name,
                "quantity": item.qty,
                "price": item.rate
            }
            lines.append(line_item)

        if doc.total_taxes_and_charges:
            lines.append({
                "tax": doc.total_taxes_and_charges
            })

        # Create payload
        payload = {
            "communicationConfig": {
                "emailsTo": [doc.owner]
            },
            "amount": doc.grand_total,
            "currency": doc.currency,
            "buyer": {
                "employee": {
                    "email": doc.modified_by
                },
                "email": doc.contact_email,
                "first_name": doc.contact_person,
                "phone": doc.contact_mobile,
                "draft": False,
            },
            "plan": { 
                "planType": "invoice"
            },
            "lines": lines,
            "externalReferenceId": doc.name,
            "shippingAddress": doc.shipping_address,
            "totalDiscount": doc.discount_amount or 0,
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