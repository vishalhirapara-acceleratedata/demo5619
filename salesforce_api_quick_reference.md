# Salesforce API Quick Reference Guide

## Decision Tree: Which API to Use?

```
START: How many records are you processing?
│
├─ < 200 records
│  └─ Use REST API (Individual or SObject Collections)
│
├─ 200-2,000 records  
│  ├─ Real-time needed? → REST API (SObject Collections)
│  └─ Batch processing OK? → Consider Bulk API 2.0
│
└─ > 2,000 records
   └─ Use Bulk API 2.0
```

## Quick Setup Checklist

### Prerequisites
- [ ] Salesforce org with API access enabled
- [ ] Connected App created with OAuth settings
- [ ] User has "API Enabled" permission
- [ ] Client credentials (Consumer Key/Secret)

### Authentication Quick Start
```python
# Username-Password Flow (Simple)
import requests

auth_data = {
    'grant_type': 'password',
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET', 
    'username': 'your.email@domain.com',
    'password': 'your_password_and_security_token'
}

response = requests.post(
    'https://login.salesforce.com/services/oauth2/token',
    data=auth_data
)

auth = response.json()
access_token = auth['access_token']
instance_url = auth['instance_url']
```

## REST API Quick Commands

### Single Record Operations
```python
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

# Create
response = requests.post(
    f'{instance_url}/services/data/v61.0/sobjects/Account/',
    json={'Name': 'Test Account'},
    headers=headers
)

# Read
response = requests.get(
    f'{instance_url}/services/data/v61.0/sobjects/Account/{record_id}',
    headers=headers
)

# Update  
response = requests.patch(
    f'{instance_url}/services/data/v61.0/sobjects/Account/{record_id}',
    json={'Name': 'Updated Account'},
    headers=headers
)

# Delete
response = requests.delete(
    f'{instance_url}/services/data/v61.0/sobjects/Account/{record_id}',
    headers=headers
)
```

### Bulk Operations (SObject Collections)
```python
# Up to 200 records
records_data = {
    "allOrNone": False,
    "records": [
        {"attributes": {"type": "Account"}, "Name": "Account 1"},
        {"attributes": {"type": "Account"}, "Name": "Account 2"}
    ]
}

response = requests.post(
    f'{instance_url}/services/data/v61.0/composite/sobjects',
    json=records_data,
    headers=headers
)
```

### Query (SOQL)
```python
# Simple query
query = "SELECT Id, Name FROM Account LIMIT 10"
response = requests.get(
    f'{instance_url}/services/data/v61.0/query/',
    params={'q': query},
    headers=headers
)
```

## Bulk API 2.0 Quick Commands

### Step 1: Create Job
```python
job_data = {
    "object": "Account",
    "operation": "insert",  # insert, update, upsert, delete
    "lineEnding": "LF"
}

response = requests.post(
    f'{instance_url}/services/data/v61.0/jobs/ingest',
    json=job_data,
    headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
)

job_id = response.json()['id']
```

### Step 2: Upload Data
```python
csv_data = """Name,Type,Industry
"Acme Corp","Customer","Technology"
"Beta Inc","Partner","Manufacturing" """

response = requests.put(
    f'{instance_url}/services/data/v61.0/jobs/ingest/{job_id}/batches',
    data=csv_data.encode('utf-8'),
    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'text/csv',
        'Accept': 'application/json'
    }
)
```

### Step 3: Close Job
```python
response = requests.patch(
    f'{instance_url}/services/data/v61.0/jobs/ingest/{job_id}',
    json={"state": "UploadComplete"},
    headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
)
```

### Step 4: Monitor Job
```python
import time

while True:
    response = requests.get(
        f'{instance_url}/services/data/v61.0/jobs/ingest/{job_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    status = response.json()['state']
    if status in ['JobComplete', 'Failed', 'Aborted']:
        break
    
    time.sleep(30)  # Wait 30 seconds
```

## Common Data Formats

### CSV Format (Bulk API)
```csv
Name,Type,Industry,Annual_Revenue__c
"Acme Corporation","Customer","Technology",1000000
"Beta Industries","Partner","Manufacturing",2500000
```

### JSON Format (REST API)
```json
{
  "Name": "Acme Corporation",
  "Type": "Customer", 
  "Industry": "Technology",
  "Annual_Revenue__c": 1000000
}
```

## Error Handling Patterns

### REST API Error Handling
```python
response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    # Success
    result = response.json()
elif response.status_code == 429:
    # Rate limited - wait and retry
    time.sleep(60)
    # Retry logic here
else:
    # Handle error
    error_details = response.json()
    print(f"Error: {error_details}")
```

### Bulk API Error Handling
```python
# Get failed records
response = requests.get(
    f'{instance_url}/services/data/v61.0/jobs/ingest/{job_id}/failedResults',
    headers={'Authorization': f'Bearer {access_token}', 'Accept': 'text/csv'}
)

failed_records_csv = response.text
# Process failed records for retry
```

## Performance Optimization Tips

### Batch Size Guidelines
| API Type | Optimal Batch Size | Maximum |
|----------|-------------------|---------|
| REST Single | 1 record | 1 record |
| REST SObject Collections | 200 records | 200 records |
| REST Composite | 25 subrequests | 25 subrequests |
| Bulk API CSV | 5,000-10,000 records | 10,000 records |
| Bulk API JSON | 2,000-5,000 records | 10,000 records |

### Rate Limit Management
```python
# Check remaining API calls
response = requests.get(
    f'{instance_url}/services/data/v61.0/limits',
    headers=headers
)

limits = response.json()
daily_api_requests = limits['DailyApiRequests']
print(f"Used: {daily_api_requests['Used']} / {daily_api_requests['Max']}")
```

## Common Use Cases & Recommendations

### Data Migration (Large Volume)
```python
# Use Bulk API 2.0
# - 10,000 records per batch
# - CSV format for performance
# - Monitor job status
# - Handle failed records separately
```

### Real-time Integration
```python
# Use REST API
# - Individual calls for immediate response
# - SObject Collections for small batches
# - Implement retry logic for rate limits
```

### ETL Process (Regular Batches)
```python
# Use Bulk API 2.0 with upsert
# - External ID field for deduplication
# - Process in off-peak hours
# - Schedule regular monitoring
```

### Web Application Integration
```python
# Use REST API
# - OAuth Web Server flow
# - Cache access tokens
# - Handle user context properly
```

## Testing & Debugging

### Test in Sandbox First
```python
# Change base URL for sandbox
base_url = "https://test.salesforce.com"  # Sandbox
# base_url = "https://login.salesforce.com"  # Production
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show all HTTP requests/responses
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|--------|----------|
| `INVALID_LOGIN` | Bad credentials | Check username/password/token |
| `REQUEST_LIMIT_EXCEEDED` | API limit reached | Wait for reset or increase limits |
| `INSUFFICIENT_ACCESS` | Missing permissions | Check user permissions and profiles |
| `ENTITY_IS_DELETED` | Record not found | Verify record ID exists |

## Monitoring & Alerting

### Key Metrics to Track
- API calls used vs. limit
- Job success/failure rates  
- Processing times
- Error types and frequency

### Simple Monitoring Script
```python
def check_api_limits():
    response = requests.get(f'{instance_url}/services/data/v61.0/limits', headers=headers)
    limits = response.json()
    
    api_usage = limits['DailyApiRequests']
    usage_percent = (api_usage['Used'] / api_usage['Max']) * 100
    
    if usage_percent > 80:
        print(f"WARNING: API usage at {usage_percent:.1f}%")
    
    return usage_percent
```

## Quick Troubleshooting

### Authentication Issues
1. Verify credentials in Salesforce
2. Check Connected App settings
3. Ensure user has API access
4. Validate security token (if using Username-Password flow)

### Rate Limit Issues
1. Check current usage with `/limits` endpoint
2. Implement exponential backoff
3. Consider upgrading Salesforce edition
4. Optimize API call efficiency

### Data Issues
1. Validate data format matches Salesforce field types
2. Check required fields are included
3. Verify lookup relationships exist
4. Test with small dataset first

This quick reference should help you get started quickly with either API approach based on your specific requirements.