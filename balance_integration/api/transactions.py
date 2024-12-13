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
        line_items = []
        for item in doc.items:
            if not item.qty or not item.rate:
                frappe.throw(_("Item quantity and rate are required"))
                
            line_item = {
                "title": item.item_name or item.item_code,
                "quantity": float(item.qty),
                "price": float(item.rate)
            }
            line_items.append(line_item)

        # Create lines array with a single object containing both lineItems and tax
        lines = [{
            "lineItems": line_items,
            "tax": float(doc.total_taxes_and_charges) if doc.total_taxes_and_charges else 0
        }]

        # Format the posting date as ISO string
        charge_date = doc.posting_date.strftime("%Y-%m-%d") if doc.posting_date else None

        # Create payload
        payload = {
            "communicationConfig": {
                "emailsTo": [customer.email_id]
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
                "planType": "invoice",
                "chargeDate": charge_date
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
            "netDaysOptions": [60, 30],
            "allowedPaymentMethods": ["payWithTerms", "creditCard"],
            "allowedTermsPaymentMethods": ["creditCard", "achDebit"],
            "marketplaceFixedTake": 0,
            "autoPayouts": False,
            "statementDescriptor": {
                "charge": "ERPNext Invoice"
            },
            "notes": "Balance Invoice Processed via ERPNext"
        }
        
        # Make API request
        endpoint = f"{settings.api_base_url}/transactions"
        return make_request("POST", endpoint, settings.api_key, payload)
        
    except Exception as e:
        frappe.log_error(f"Error creating Balance transaction: {str(e)}")
        raise

def generate_buyer_token(buyer_id, settings):
    """Generate a buyer token for Balance"""
    if not buyer_id:
        frappe.throw(_("Buyer ID is required"))
    endpoint = f"{settings.api_base_url}/buyers/{buyer_id}/token"

    payload = {
        "scope": "ADD_PAYMENT_METHOD"
    }
    try:
        result = make_request("POST", endpoint, settings.api_key, payload)
        if result and result.get('token'):
            return result['token']
        else:
            frappe.throw(_("Failed to generate buyer token"))

    except Exception as e:
        frappe.log_error(f"Error generating buyer token: {str(e)}")
        raise

def confirm_transaction(transaction_id, buyer_id, settings):
    """Confirm a Balance transaction"""
    if not transaction_id:
        frappe.throw(_("Transaction ID is required"))

    if not buyer_id:
        frappe.throw(_("Buyer ID is required"))

    token = generate_buyer_token(buyer_id, settings)
    if not token:
        frappe.throw(_("Failed to generate buyer token"))
        
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/confirm"
    
    # Required payload for confirm endpoint
    payload = {
        "paymentMethodType": "payWithTerms",
        "isAuth": False,
        "isFinanced": False,
        "paymentMethodId": token,
        "termsNetDays": 60
    }
    
    try:
        result = make_request("POST", endpoint, settings.api_key, payload)
        if result and result.get('status') == 'confirmed':
            return result
        else:
            frappe.throw(_("Failed to confirm transaction"))
    except Exception as e:
        frappe.throw(_("Error confirming transaction: {0}").format(str(e)[:140]))

def capture_transaction(transaction_id, settings):
    """Capture a Balance transaction"""
    endpoint = f"{settings.api_base_url}/transactions/{transaction_id}/capture"
    return make_request("POST", endpoint, settings.api_key)