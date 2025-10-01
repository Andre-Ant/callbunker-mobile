# Backend Integration Guide

How the CallBunker mobile app connects to your backend server.

## Backend Architecture

The app uses a multi-user REST API architecture where each user is isolated with their own:
- Unique CallBunker phone number (from phone pool)
- Call history
- Trusted contacts
- Message logs

## API Base URL Configuration

### Development

Edit `src/services/CallBunkerContext.js`:

```javascript
// Line 14
const API_BASE_URL = 'http://localhost:5000';  // For local testing

// Or use ngrok/localtunnel for device testing
const API_BASE_URL = 'https://abc123.ngrok.io';
```

### Production

```javascript
const API_BASE_URL = 'https://your-backend.repl.co';
// Or your custom domain
const API_BASE_URL = 'https://api.callbunker.com';
```

## API Endpoints Used

### Authentication & User Management

#### POST `/multi/signup`
Create new user and assign phone number from pool.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123,
  "defense_number": "+16315551234",
  "message": "Account created successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Email already registered"
}
```

#### GET `/multi/user/{userId}/info`
Get user details and configuration.

**Response:**
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "defense_number": "+16315551234",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### Protected Calling

#### POST `/multi/user/{userId}/call_direct`
Get call configuration for native calling.

**Request:**
```json
{
  "to_number": "+15558887777"
}
```

**Response:**
```json
{
  "success": true,
  "call_log_id": 456,
  "target_number": "+15558887777",
  "twilio_caller_id": "+16315551234",
  "user_defense_number": "+16315551234"
}
```

**What happens:**
1. Backend creates call log entry
2. Returns target number (what to dial)
3. Returns Twilio caller ID (what recipient sees)
4. App opens native dialer with target number
5. Recipient sees CallBunker number as caller ID

#### POST `/multi/user/{userId}/calls/{callId}/complete`
Log call completion and duration.

**Request:**
```json
{
  "status": "completed",
  "duration_seconds": 245
}
```

**Response:**
```json
{
  "success": true,
  "call_log_id": 456,
  "duration": 245
}
```

#### GET `/multi/user/{userId}/calls`
Retrieve call history.

**Query Parameters:**
- `limit` (optional): Number of records (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "calls": [
    {
      "id": 456,
      "to_number": "+15558887777",
      "from_number": "+16315551234",
      "direction": "outbound",
      "status": "completed",
      "duration_seconds": 245,
      "timestamp": "2025-01-15T14:22:00Z",
      "caller_id_shown": "+16315551234"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### Trusted Contacts Management

#### GET `/multi/user/{userId}/contacts`
List all trusted contacts.

**Response:**
```json
{
  "contacts": [
    {
      "id": 789,
      "phone_number": "+15559998888",
      "name": "Mom",
      "custom_pin": "1234",
      "created_at": "2025-01-10T08:00:00Z"
    }
  ]
}
```

#### POST `/multi/user/{userId}/contacts`
Add new trusted contact.

**Request:**
```json
{
  "phone_number": "+15559998888",
  "name": "Mom",
  "custom_pin": "1234"
}
```

**Response:**
```json
{
  "success": true,
  "contact_id": 789,
  "message": "Contact added to whitelist"
}
```

#### DELETE `/multi/user/{userId}/contacts/{contactId}`
Remove trusted contact.

**Response:**
```json
{
  "success": true,
  "message": "Contact removed"
}
```

---

### Anonymous Messaging

#### POST `/multi/user/{userId}/send_message`
Send SMS from CallBunker number.

**Request:**
```json
{
  "to_number": "+15558887777",
  "message": "This is an anonymous message from CallBunker"
}
```

**Response:**
```json
{
  "success": true,
  "message_sid": "SM1234567890abcdef",
  "from": "+16315551234",
  "to": "+15558887777",
  "status": "sent"
}
```

---

## Error Handling

All endpoints may return error responses:

**Format:**
```json
{
  "success": false,
  "error": "Detailed error message",
  "code": "ERROR_CODE"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (invalid user ID)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error (backend issue)

**App Error Handling:**
```javascript
try {
  const response = await fetch(`${API_BASE_URL}/multi/user/${userId}/info`);
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Unknown error');
  }
  
  return data;
} catch (error) {
  console.error('API Error:', error);
  Alert.alert('Error', error.message);
}
```

---

## Phone Pool Requirements

For the app to work, backend must have:

### 1. Phone Pool Setup
- Minimum 10 available Twilio numbers
- Automatic replenishment configured
- Threshold monitoring active

### 2. Admin Dashboard
- Access at `/admin/phones/login`
- Monitor pool status
- Manually replenish if needed

### 3. Twilio Configuration
- Valid Twilio credentials in environment
- Numbers configured with webhooks
- SMS and Voice capabilities enabled

**Check pool status:**
```bash
curl https://your-backend.repl.co/admin/phones/api/status \
  -H "X-Admin-API-Key: YOUR_ADMIN_KEY"
```

**Response:**
```json
{
  "available": 15,
  "assigned": 5,
  "total": 20,
  "threshold": 10,
  "needs_replenishment": false
}
```

---

## Environment Variables (Backend)

Ensure these are set on your backend:

```bash
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx

# Database
DATABASE_URL=postgresql://...

# App
PUBLIC_APP_URL=https://your-backend.repl.co
SESSION_SECRET=random-secret-key
ADMIN_API_KEY=admin-api-key-for-dashboard
```

---

## Testing Backend Integration

### 1. Test Connection

```javascript
// In app, test basic connectivity
fetch('https://your-backend.repl.co/health')
  .then(r => r.json())
  .then(data => console.log('Backend healthy:', data));
```

### 2. Test Signup

```javascript
const testSignup = async () => {
  const response = await fetch('https://your-backend.repl.co/multi/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Test User',
      email: 'test@example.com'
    })
  });
  
  const data = await response.json();
  console.log('Signup result:', data);
  // Should return: { success: true, user_id: X, defense_number: "+1..." }
};
```

### 3. Test Calling

```javascript
const testCall = async (userId) => {
  const response = await fetch(`https://your-backend.repl.co/multi/user/${userId}/call_direct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to_number: '+15558887777'
    })
  });
  
  const data = await response.json();
  console.log('Call config:', data);
  // Should return call configuration with target_number and twilio_caller_id
};
```

---

## Development vs Production

### Development Mode

```javascript
// In CallBunkerContext.js
const USE_MOCK_DATA = true;  // Use fake data for UI testing

// Mock responses are returned locally
// No backend calls made
// Great for UI/UX development
```

### Production Mode

```javascript
const USE_MOCK_DATA = false;  // Use real backend
const API_BASE_URL = 'https://your-production-backend.com';

// All calls go to real backend
// Twilio numbers assigned
// Real SMS/calls made
```

---

## Webhook Configuration

Backend webhooks handle incoming calls/SMS to CallBunker numbers.

**Required Webhooks:**

1. **Voice Webhook** - Incoming calls
   - URL: `https://your-backend.repl.co/voice/incoming`
   - Method: POST
   - Handles: Call screening, PIN authentication

2. **SMS Webhook** - Incoming messages
   - URL: `https://your-backend.repl.co/sms/incoming`
   - Method: POST  
   - Handles: Message forwarding, auto-replies

These are configured automatically by the phone provisioning system.

---

## Security Considerations

### Client-Side
- User ID stored in AsyncStorage (encrypted by OS)
- No API keys in app code
- Backend handles all Twilio auth

### Backend
- Validate user ID on every request
- Rate limit API endpoints
- Sanitize phone numbers
- Secure admin dashboard with API key

### Network
- Use HTTPS for all API calls
- Validate SSL certificates
- Handle network failures gracefully

---

## Debugging Backend Issues

### Connection Failed

```bash
# Test from terminal
curl https://your-backend.repl.co/health

# Expected response:
{"status": "healthy", "timestamp": "..."}
```

### Signup Failed

```bash
# Check phone pool
curl https://your-backend.repl.co/admin/phones/api/status \
  -H "X-Admin-API-Key: YOUR_KEY"

# If available < 1, replenish pool:
curl -X POST https://your-backend.repl.co/admin/phones/api/replenish \
  -H "X-Admin-API-Key: YOUR_KEY"
```

### Call Failed

- Verify Twilio account balance
- Check number has Voice capability
- Ensure webhooks configured
- Review backend logs for errors

---

## Quick Integration Checklist

Before deploying mobile app:

- [ ] Backend deployed and accessible
- [ ] Phone pool has 10+ available numbers
- [ ] Twilio credentials configured
- [ ] Admin API key set
- [ ] Test signup creates user + assigns number
- [ ] Test call returns valid configuration
- [ ] Test call history retrieves records
- [ ] Test contacts CRUD operations
- [ ] Test message sending works
- [ ] Webhooks configured on all pool numbers
- [ ] SSL certificate valid (HTTPS working)

---

**Your backend is ready when all API endpoints return successful responses!**

For backend setup, see the main CallBunker backend repository's documentation.
