# WhatsApp Integration Setup

This guide explains how to set up WhatsApp Business API integration for bulk messaging.

## Features

- 📱 Bulk send WhatsApp messages to customers
- 🔍 Filter customers by city and sales representative
- ✅ Select specific customers or send to all
- 📊 View customer list with phone numbers
- 🚀 Real-time messaging status updates

## Prerequisites

1. **WhatsApp Business API Account**
   - Meta Business Account
   - WhatsApp Business API access
   - Phone number ID
   - Access token

## Setup Instructions

### Step 1: Get WhatsApp Business API Credentials

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create or select your app
3. Add WhatsApp product to your app
4. Go to **WhatsApp > API Setup**
5. Copy the following:
   - **Phone number ID** (e.g., `850720011454978`)
   - **Access token** (temporary or permanent)
   - **API Version** (default: `v21.0`)

### Step 2: Configure Environment Variables

#### Option 1: Environment Variables (Recommended)

Set these environment variables:

```bash
export WHATSAPP_PHONE_NUMBER_ID="your_phone_number_id"
export WHATSAPP_ACCESS_TOKEN="your_access_token"
export WHATSAPP_API_VERSION="v21.0"
```

#### Option 2: Docker Compose

Add to your `docker-compose.yml`:

```yaml
environment:
  - WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
  - WHATSAPP_ACCESS_TOKEN=your_access_token
  - WHATSAPP_API_VERSION=v21.0
```

#### Option 3: .env File

Create a `.env` file:

```env
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_API_VERSION=v21.0
```

### Step 3: Update app.py (Optional)

You can also hardcode the credentials in `whatsapp_service.py`:

```python
WHATSAPP_PHONE_NUMBER_ID = 'your_phone_number_id'
WHATSAPP_ACCESS_TOKEN = 'your_access_token'
WHATSAPP_API_VERSION = 'v21.0'
```

## Usage

### Access the Customers Page

1. Navigate to the main page: `http://localhost:5000`
2. Click "View Customers & Send WhatsApp"
3. Or go directly to: `http://localhost:5000/customers`

### Filter Customers

1. Select **City** (default: Patna)
2. Select **Sales Representative** (Manas, Satyam, Ankit, or All)
3. Click **Load Customers**

### Send WhatsApp Messages

1. **Select Customers:**
   - Use checkboxes to select individual customers
   - Click "Select All" to select all customers with phone numbers
   - Click "Deselect All" to clear selection

2. **Send Message:**
   - Click "Send WhatsApp" button
   - Enter your message in the modal
   - Click "Send Messages"

3. **View Results:**
   - Success/failure counts are displayed
   - Individual message status is tracked

## Phone Number Format

- Phone numbers are automatically cleaned and formatted
- Supports Indian phone numbers (with country code 91)
- Removes spaces, dashes, parentheses, and plus signs
- Validates minimum length (10 digits)

## Rate Limiting

- Default delay: 2 seconds between messages
- Adjustable in `whatsapp_service.py`
- Prevents API rate limiting issues

## Error Handling

The system handles:
- Invalid phone numbers (skipped)
- API errors (logged and reported)
- Network issues (retry logic)
- Missing credentials (clear error messages)

## Security Notes

⚠️ **Important:**
- Never commit access tokens to version control
- Use environment variables for credentials
- Rotate access tokens regularly
- Use permanent tokens for production
- Monitor API usage and limits

## Troubleshooting

### Messages Not Sending

1. **Check Credentials:**
   - Verify phone number ID is correct
   - Verify access token is valid and not expired
   - Check API version is correct

2. **Check Phone Numbers:**
   - Ensure phone numbers are valid
   - Check format (should be 10+ digits)
   - Verify country code is included

3. **Check API Status:**
   - Verify WhatsApp Business API is active
   - Check Meta Business account status
   - Review API usage limits

### API Errors

Common errors:
- **401 Unauthorized:** Invalid access token
- **403 Forbidden:** Insufficient permissions
- **429 Too Many Requests:** Rate limit exceeded
- **400 Bad Request:** Invalid phone number format

### Debug Mode

Enable debug logging in `whatsapp_service.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Limits

WhatsApp Business API has rate limits:
- **Tier 1:** 1,000 messages per day
- **Tier 2:** 10,000 messages per day
- **Tier 3:** 100,000 messages per day

Check your tier in Meta Business Manager.

## Support

For issues:
1. Check Meta Business API documentation
2. Review error messages in the application
3. Check WhatsApp Business API status page
4. Contact Meta Business support

## Additional Resources

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Business API Setup Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)

