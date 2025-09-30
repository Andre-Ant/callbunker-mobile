# CallBunker Phone Provisioning System

## Overview

The hybrid phone provisioning system automatically maintains a pool of 20-50 Twilio phone numbers ready for instant user assignment. This eliminates signup delays while optimizing costs through bulk purchasing.

## System Architecture

### Components

1. **PhoneProvisioning Utility** (`utils/phone_provisioning.py`)
   - Purchases Twilio numbers via API
   - Configures webhooks automatically
   - Handles batch operations
   - Implements database locking for concurrency control

2. **Admin Dashboard** (`/admin/phones/dashboard`)
   - Real-time pool monitoring
   - Manual purchase controls
   - Recent assignment tracking
   - Webhook configuration tools

3. **Automatic Threshold Monitoring** (integrated in signup flow)
   - Triggers background replenishment when pool drops below 10
   - Emergency fallback if pool empty during signup

4. **Background Replenishment Job** (`/admin/phones/cron/auto-replenish`)
   - Scheduled job for automated replenishment
   - Concurrency-safe with PostgreSQL advisory locks
   - Can be called by external schedulers

## Configuration

### Pool Settings

Configure in `utils/phone_provisioning.py`:

```python
POOL_THRESHOLD_LOW = 10       # Trigger replenishment below this
REPLENISHMENT_BATCH_SIZE = 10  # Purchase this many at once
```

### Security

All admin endpoints require authentication via:

1. **Admin Session** - Flask session with `admin_authenticated=True`
2. **API Key** - Pass in header `X-Admin-API-Key` or query param `api_key`

**Required Secret**: Set `ADMIN_API_KEY` in environment variables

## Usage

### 1. Admin Dashboard Access

```
https://your-domain.com/admin/phones/dashboard
```

Requires: `ADMIN_API_KEY` in header or session authentication

### 2. Manual Phone Purchase

**Via Dashboard:**
- Click "Purchase Numbers"
- Specify count and optional area code
- System purchases and configures webhooks

**Via API:**
```bash
curl -X POST https://your-domain.com/admin/phones/api/purchase \
  -H "X-Admin-API-Key: your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "area_code": "415"}'
```

### 3. Trigger Manual Replenishment

```bash
curl -X POST https://your-domain.com/admin/phones/api/replenish \
  -H "X-Admin-API-Key: your_key_here"
```

Response:
```json
{
  "replenished": true,
  "purchased_count": 10,
  "previous_status": {"available": 5, "assigned": 15, "total": 20},
  "new_status": {"available": 15, "assigned": 15, "total": 30}
}
```

### 4. Automated Replenishment (Cron)

Schedule with external service (e.g., cron, GitHub Actions):

```bash
# Run every hour
curl -X POST https://your-domain.com/admin/phones/cron/auto-replenish?api_key=your_key_here
```

Or set up Replit Cron (if available):
- Frequency: Hourly
- Endpoint: `/admin/phones/cron/auto-replenish`
- Method: POST
- Headers: `X-Admin-API-Key: your_key_here`

## How It Works

### User Signup Flow

1. User submits signup form
2. System queries pool for available number with `SELECT ... FOR UPDATE` (row lock)
3. If available: assigns immediately
4. If pool < threshold: triggers async background replenishment
5. If pool empty: emergency purchase with fallback protection

### Automatic Replenishment

1. Cron job calls `/admin/phones/cron/auto-replenish`
2. System acquires PostgreSQL advisory lock (prevents concurrent runs)
3. Checks pool status
4. If below threshold: purchases batch of numbers
5. Releases lock
6. Returns status report

### Concurrency Protection

**Database Advisory Lock:**
```python
# Prevents duplicate purchases across processes
pg_try_advisory_lock(12345)  # Non-blocking attempt
```

**Row-Level Locking:**
```python
# Prevents race conditions during assignment
SELECT ... FOR UPDATE
```

## Monitoring

### Pool Status API

```bash
curl https://your-domain.com/admin/phones/api/status \
  -H "X-Admin-API-Key: your_key_here"
```

Response:
```json
{
  "available": 15,
  "assigned": 10,
  "total": 25,
  "threshold": 10,
  "needs_replenishment": false
}
```

### Dashboard Features

- **Real-time Statistics**: Available, assigned, total counts
- **Recent Assignments**: Last 10 number assignments with timestamps
- **Available Pool**: All unassigned numbers ready for use
- **Webhook Status**: Configuration status for each number

## Cost Management

### Estimated Costs

- **Per Number**: ~$1.00/month (Twilio local number)
- **Pool of 20-50**: $20-50/month baseline
- **SMS/Voice**: Pay per use (separate from number cost)

### Optimization Strategies

1. **Threshold Tuning**: Adjust `POOL_THRESHOLD_LOW` based on signup rate
2. **Batch Size**: Larger batches reduce API calls but increase idle inventory
3. **Area Code Strategy**: Specific area codes may have different pricing

## Troubleshooting

### No Numbers Available

**Symptom**: Signup fails with "No available numbers in pool"

**Solution**:
1. Check pool status in admin dashboard
2. Trigger manual replenishment
3. Verify Twilio account has available numbers in desired region
4. Check Twilio account balance

### Duplicate Purchases

**Symptom**: Multiple concurrent replenishments purchase too many numbers

**Solution**: Already protected! System uses PostgreSQL advisory locks to prevent this.

### Webhook Configuration Failed

**Symptom**: Numbers purchased but webhooks not configured

**Solution**:
1. Verify `PUBLIC_APP_URL` is set correctly
2. Run manual webhook configuration:
```bash
curl -X POST https://your-domain.com/admin/phones/api/configure-webhooks \
  -H "X-Admin-API-Key: your_key_here"
```

### Twilio API Errors

**Common Issues**:
- Insufficient balance
- Geographic permissions not enabled
- Area code unavailable
- API rate limiting

**Check Logs**: Application logs show detailed Twilio API responses

## Security Best Practices

1. **Protect Admin Key**: Never commit `ADMIN_API_KEY` to version control
2. **Use HTTPS**: All admin endpoints should be accessed over HTTPS
3. **Rotate Keys**: Periodically update `ADMIN_API_KEY`
4. **Monitor Access**: Log all admin API calls for audit trail
5. **Rate Limiting**: Consider adding rate limits to purchase endpoints

## Integration Examples

### GitHub Actions (Hourly Replenishment)

```yaml
name: Replenish Phone Pool
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
jobs:
  replenish:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Replenishment
        run: |
          curl -X POST ${{ secrets.APP_URL }}/admin/phones/cron/auto-replenish \
            -H "X-Admin-API-Key: ${{ secrets.ADMIN_API_KEY }}"
```

### External Cron Service

Most cron services (EasyCron, cron-job.org) support:
- URL: `https://your-domain.com/admin/phones/cron/auto-replenish`
- Method: POST
- Headers: `X-Admin-API-Key: your_key_here`
- Frequency: Every 1-6 hours (based on traffic)

## Future Enhancements

Potential improvements:
- Email/SMS alerts when pool critically low
- Cost tracking and reporting dashboard
- Multi-region pool support
- Number recycling for inactive users
- Predictive replenishment based on signup patterns
