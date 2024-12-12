# Balance Integration

Integration between ERPNext and Balance Payment System.

## Features

- Automatically create and process Balance transactions when Sales Invoices are submitted
- Create Balance credit notes when Credit Notes are submitted
- Send qualification links to customers
- Configurable API endpoints for sandbox/production environments

## Installation

1. From your bench directory, run:
```bash
bench get-app https://github.com/your-repo/balance_integration
bench --site your-site install-app balance_integration
bench --site your-site migrate
```

2. Configure Balance Settings:
   - Go to Balance Settings in ERPNext
   - Enter your Balance API Key
   - The default API Base URL is set to sandbox: `https://api.sandbox.getbalance.com/v1`
   - Save the settings

## Usage

### Sales Invoice Integration
When a Sales Invoice is submitted, the app will:
1. Create a Balance transaction
2. Confirm the transaction
3. Capture the transaction
4. Store the Balance transaction ID in the Sales Invoice

### Credit Note Integration
When a Credit Note is submitted, the app will automatically create a corresponding credit note in Balance.

### Sending Qualification Links
To send a qualification link to a customer:
1. Open the Customer document
2. Click on "Send Balance Qualification Link"
3. The link will be sent to the customer's email address

## Development

For local development:
1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT