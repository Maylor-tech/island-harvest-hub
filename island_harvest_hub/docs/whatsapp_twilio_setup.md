# WhatsApp Business Integration with Twilio - Setup Guide

This guide will walk you through setting up WhatsApp Business integration using Twilio for Island Harvest Hub.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Create Twilio Account](#step-1-create-twilio-account)
3. [Step 2: Set Up WhatsApp Sandbox](#step-2-set-up-whatsapp-sandbox)
4. [Step 3: Get Your Credentials](#step-3-get-your-credentials)
5. [Step 4: Configure the Application](#step-4-configure-the-application)
6. [Step 5: Test the Integration](#step-5-test-the-integration)
7. [Step 6: Create Message Templates (Production)](#step-6-create-message-templates-production)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A Twilio account (free trial available)
- A phone number that can receive SMS/WhatsApp messages for testing
- Access to your Island Harvest Hub application files

---

## Step 1: Create Twilio Account

1. **Visit Twilio Website**
   - Go to [https://www.twilio.com](https://www.twilio.com)
   - Click "Sign Up" or "Get Started Free"

2. **Sign Up Process**
   - Enter your email address
   - Create a password
   - Verify your email address
   - Complete the account setup form

3. **Verify Your Phone Number**
   - Twilio will send a verification code to your phone
   - Enter the code to verify your number

4. **Complete Account Setup**
   - Fill in your business information
   - Choose your use case (select "Customer Communications" or "Business Messaging")
   - Complete the setup wizard

---

## Step 2: Set Up WhatsApp Sandbox

The WhatsApp Sandbox allows you to test WhatsApp messaging without going through the full WhatsApp Business API approval process.

### 2.1 Access WhatsApp Sandbox

1. **Navigate to WhatsApp in Twilio Console**
   - Log in to your Twilio Console: [https://console.twilio.com](https://console.twilio.com)
   - In the left sidebar, click on "Messaging"
   - Click on "Try it out" → "Send a WhatsApp message"
   - Or navigate directly to: [https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)

2. **Join the Sandbox**
   - You'll see a WhatsApp sandbox number (format: `whatsapp:+14155238886`)
   - You'll also see a join code (e.g., `join <code-word>`)
   - Open WhatsApp on your phone
   - Send the join code to the sandbox number
   - Example: Send `join example-code` to `+1 415 523 8886`

3. **Verify Sandbox Connection**
   - Once you send the join code, you'll receive a confirmation message
   - Your phone number is now connected to the Twilio WhatsApp Sandbox

### 2.2 Add Additional Test Numbers

To test with multiple numbers (e.g., customer phone numbers):

1. In the WhatsApp Sandbox page, find the "Sandbox Participants" section
2. Click "Add participant"
3. Enter the phone number (in E.164 format: +1876XXXXXXXX)
4. That person needs to send the join code to the sandbox number from their WhatsApp

---

## Step 3: Get Your Credentials

You'll need three pieces of information from your Twilio account:

### 3.1 Account SID

1. In Twilio Console, go to the Dashboard
2. Your **Account SID** is displayed at the top of the page
   - Format: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Copy this value

### 3.2 Auth Token

1. In Twilio Console, go to the Dashboard
2. Click on "Auth Token" (it will be hidden, click "View" to reveal it)
3. Copy the **Auth Token**
   - Format: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ **Keep this secret!** Never share it publicly

### 3.3 WhatsApp Sandbox Number

1. Go to Messaging → Try it out → Send a WhatsApp message
2. Your **WhatsApp Sandbox Number** is displayed
   - Format: `whatsapp:+14155238886` or just `+14155238886`
   - Copy this number

---

## Step 4: Configure the Application

### 4.1 Update Configuration File

1. **Locate the Configuration File**
   - Open `whatsapp_config.json` in the project root directory

2. **Update the Configuration**
   ```json
   {
       "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
       "auth_token": "your_auth_token_here",
       "twilio_whatsapp_number": "+14155238886",
       "enable_whatsapp": true,
       "debug": true
   }
   ```

3. **Fill in Your Credentials**
   - Replace `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your Account SID
   - Replace `your_auth_token_here` with your Auth Token
   - Replace `+14155238886` with your WhatsApp Sandbox Number
   - Set `enable_whatsapp` to `true` to enable WhatsApp messaging
   - Set `debug` to `true` for detailed logging (set to `false` in production)

### 4.2 Install Dependencies

Make sure the Twilio Python library is installed:

```bash
pip install twilio>=8.10.0
```

Or if using requirements.txt:

```bash
pip install -r requirements.txt
```

---

## Step 5: Test the Integration

### 5.1 Test via Application UI

1. **Start the Application**
   ```bash
   streamlit run island_harvest_hub/main.py
   ```

2. **Navigate to Customer Management**
   - Click on "👥 Customer Management" in the sidebar
   - Find a customer with a phone number
   - Click the "💬 WhatsApp" button

3. **Send a Test Message**
   - Select "Custom Message"
   - Enter a test message
   - Click "Send Message"
   - Check your WhatsApp for the message

### 5.2 Test via Python Script

Create a test script `test_whatsapp.py`:

```python
from app.services.whatsapp_automation_service import WhatsAppAutomationService

# Initialize service
whatsapp_service = WhatsAppAutomationService()

# Send test message
# Replace with your test phone number (must be joined to sandbox)
test_number = "+1876XXXXXXXX"  # Your phone number in E.164 format

success, message = whatsapp_service.send_test_message(test_number)
if success:
    print(f"✅ Test message sent successfully!")
    print(f"Message: {message}")
else:
    print(f"❌ Failed to send message: {message}")
```

Run the test:
```bash
python test_whatsapp.py
```

---

## Step 6: Create Message Templates (Production)

For production use, you'll need to create approved message templates through Twilio. The sandbox allows free-form messages, but production requires pre-approved templates.

### 6.1 Understanding WhatsApp Message Templates

WhatsApp requires message templates for:
- Order confirmations
- Delivery notifications
- Payment reminders
- Any automated messages

### 6.2 Create Templates via Twilio Console

1. **Navigate to Content Templates**
   - Go to Twilio Console → Messaging → Content Templates
   - Click "Create Template"

2. **Template Requirements**
   - **Name**: Unique identifier (e.g., `order_confirmation`)
   - **Category**: Choose appropriate category
   - **Language**: Select language (e.g., English)
   - **Body**: Message content with placeholders
   - **Header** (optional): Can include text or media
   - **Footer** (optional): Additional text

3. **Example Template: Order Confirmation**
   ```
   Template Name: order_confirmation
   Category: UTILITY
   Language: English (US)
   
   Body:
   Hello {{1}}! Your order #{{2}} has been confirmed. 
   Total: ${{3}}. Delivery scheduled for {{4}}.
   ```

4. **Submit for Approval**
   - Submit your template for WhatsApp approval
   - Approval typically takes 24-48 hours
   - You'll receive notification when approved

### 6.3 Update Service to Use Templates

Once templates are approved, update `whatsapp_automation_service.py` to use template messages instead of free-form messages for production.

---

## Features Implemented

### ✅ Automated Notifications

1. **Order Confirmation**
   - Automatically sent when an order is created
   - Includes order details, items, total amount, and delivery date

2. **Payment Reminder**
   - Automatically sent when an invoice is generated
   - Includes invoice number, amount, and due date

3. **Delivery Notification**
   - Can be sent manually via UI
   - Includes delivery date and time window

### ✅ Manual Messaging

1. **Custom Messages**
   - Send custom WhatsApp messages to customers
   - Available in Customer Management UI

2. **Quick Actions**
   - Send order confirmations
   - Send delivery notifications
   - Send payment reminders
   - All available from customer and invoice pages

---

## Troubleshooting

### Issue: "Twilio client not initialized"

**Solution:**
- Check that `whatsapp_config.json` exists and is properly formatted
- Verify `enable_whatsapp` is set to `true`
- Check that Account SID and Auth Token are correct

### Issue: "Message failed to send"

**Possible Causes:**
1. **Phone number not in sandbox**
   - Solution: Add the number to sandbox participants or have them join manually

2. **Invalid phone number format**
   - Solution: Ensure phone number is in E.164 format (+1876XXXXXXXX)

3. **Twilio account limits**
   - Solution: Check your Twilio account balance and limits

4. **WhatsApp sandbox restrictions**
   - Solution: In sandbox, you can only message numbers that have joined the sandbox

### Issue: "Template not found"

**Solution:**
- For sandbox: Use free-form messages (Custom Message option)
- For production: Ensure templates are created and approved in Twilio Console

### Issue: Messages not appearing in WhatsApp

**Check:**
1. Phone number is correct
2. Number has joined the WhatsApp sandbox
3. Twilio account has sufficient balance
4. Check debug logs in `database_reports/whatsapp_debug.log`

---

## Production Checklist

Before going to production:

- [ ] Upgrade from Twilio trial to paid account
- [ ] Apply for WhatsApp Business API access
- [ ] Create and get approval for message templates
- [ ] Update `whatsapp_config.json` with production credentials
- [ ] Set `debug` to `false` in configuration
- [ ] Test all message types
- [ ] Set up monitoring and error alerts
- [ ] Review Twilio pricing and set up billing alerts

---

## Twilio Pricing

### WhatsApp Sandbox (Testing)
- **Free**: Limited to sandbox participants
- **No cost** for testing within sandbox

### WhatsApp Business API (Production)
- **Per message pricing**: Varies by country
- **Template messages**: Typically $0.005 - $0.01 per message
- **Session messages**: Typically $0.005 - $0.01 per message
- Check current pricing: [Twilio WhatsApp Pricing](https://www.twilio.com/whatsapp/pricing)

---

## Additional Resources

- [Twilio WhatsApp Documentation](https://www.twilio.com/docs/whatsapp)
- [Twilio Python SDK Documentation](https://www.twilio.com/docs/libraries/python)
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Twilio Support](https://support.twilio.com/)

---

## Support

If you encounter issues:
1. Check the debug logs: `database_reports/whatsapp_debug.log`
2. Review Twilio Console for error messages
3. Check Twilio status page: [status.twilio.com](https://status.twilio.com)
4. Contact Twilio support for account-specific issues

---

**Last Updated**: 2024
**Version**: 1.0

