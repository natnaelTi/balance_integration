import frappe
from frappe import _
from balance_integration.utils import get_balance_settings, get_customer_information, get_shipping_address, get_invoice_details, make_request

"""Create a transaction in Balance"""
def create_balance_transaction(doc, settings):
    # Basic validation
    if not doc:
        frappe.throw(_("No document provided"))
        
    if not hasattr(doc, 'doctype') or doc.doctype != "Sales Invoice":
        frappe.throw(_("Invalid document type. Expected Sales Invoice"))
        
    if not hasattr(doc, 'name') or not doc.name:
        frappe.throw(_("Document must have a name"))
        
    if not hasattr(doc, 'customer') or not doc.customer:
        frappe.throw(_("Sales Invoice must have a customer"))

    if not hasattr(doc, 'shipping_address_name') or not doc.shipping_address_name:
        frappe.throw(_("Shipping address is required for Balance transaction"))

    try:
        # Get required information
        customer_info = get_customer_information(doc.customer)
        shipping_address = get_shipping_address(doc.shipping_address_name)

        # Create line items
        lines = []
        for item in doc.items:
            line_item = {
                "title": item.item_name,
                "quantity": item.qty,
                "price": item.rate
            }
            lines.append(line_item)

        if hasattr(doc, 'total_taxes_and_charges') and doc.total_taxes_and_charges:
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
                "email": customer_info["email"],
                "first_name": customer_info["customer_name"],
                "phone": customer_info["mobile_no"],
                "draft": False,
            },
            "plan": { 
                "planType": "invoice"
            },
            "lines": lines,
            "externalReferenceId": doc.name,
            "shippingAddress": shipping_address,
            "totalDiscount": doc.discount_amount if hasattr(doc, 'discount_amount') else 0,
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