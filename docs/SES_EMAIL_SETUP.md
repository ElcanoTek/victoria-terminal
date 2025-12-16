# AWS SES Email Inbox Setup for Victoria

This guide documents how to set up AWS SES (Simple Email Service) to give Victoria her own email inbox. Emails sent to the configured address are stored in S3, which Victoria can poll on demand to check for new messages and download attachments.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Incoming Email │────▶│   AWS SES   │────▶│  S3 Bucket   │────▶│   Victoria   │
│                 │     │  (Receipt)  │     │  (Storage)   │     │  (MCP Poll)  │
└─────────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
```

**How it works:**
1. Emails are sent to `anything@victoria.yourdomain.com`
2. AWS SES receives the email and saves it to an S3 bucket
3. Victoria polls the S3 bucket to check for new emails
4. Victoria can parse emails and download attachments (especially CSV files)

## Prerequisites

- AWS Account with admin access
- A domain you control (for DNS records)
- Access to your domain's DNS settings

## Step 1: Create S3 Bucket

1. Go to **AWS Console** → **S3**
2. Click **Create bucket**
3. Bucket name: `victoria-email-inbox` (or your preferred name)
4. Region: Choose your preferred region (e.g., `us-east-2`)
5. Leave all other settings as default
6. Click **Create bucket**

## Step 2: Add Bucket Policy for SES

1. Open your bucket → **Permissions** tab
2. Edit **Bucket policy** and add:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSESPuts",
      "Effect": "Allow",
      "Principal": {
        "Service": "ses.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "YOUR-AWS-ACCOUNT-ID"
        }
      }
    }
  ]
}
```

Replace `YOUR-BUCKET-NAME` and `YOUR-AWS-ACCOUNT-ID` with your actual values.

## Step 3: Create Subdomain Identity in SES

Using a subdomain keeps your main domain's email (e.g., Microsoft 365) unaffected.

1. Go to **AWS Console** → **SES** (ensure you're in the same region as your S3 bucket)
2. Click **Verified identities** → **Create identity**
3. Select **Domain**
4. Enter your subdomain: `victoria.yourdomain.com`
5. Click **Create identity**

AWS will display DNS records to add.

## Step 4: Add DNS Records

Add these records to your domain's DNS settings:

### DKIM CNAME Records (3 records)

AWS provides three CNAME records for DKIM authentication. Add all three:

| Type | Host | Value |
|------|------|-------|
| CNAME | `{token1}._domainkey.victoria` | `{token1}.dkim.amazonses.com` |
| CNAME | `{token2}._domainkey.victoria` | `{token2}.dkim.amazonses.com` |
| CNAME | `{token3}._domainkey.victoria` | `{token3}.dkim.amazonses.com` |

### MX Record

| Type | Host | Priority | Value |
|------|------|----------|-------|
| MX | `victoria` | 10 | `inbound-smtp.{region}.amazonaws.com` |

Replace `{region}` with your AWS region (e.g., `us-east-2`).

### DMARC TXT Record (Optional but Recommended)

| Type | Host | Value |
|------|------|-------|
| TXT | `_dmarc.victoria` | `v=DMARC1;p=quarantine;pct=100;fo=1` |

## Step 5: Wait for Domain Verification

DNS propagation can take 5 minutes to several hours. Check the SES console for verification status.

## Step 6: Create Receipt Rule Set

1. In SES, go to **Email receiving** → **Receipt rule sets**
2. Click **Create rule set**
3. Name: `victoria-rules`
4. Click **Create rule set**
5. **Set as active**

## Step 7: Create Receipt Rule

1. Open your rule set → **Create rule**
2. Rule name: `save-to-s3`
3. Recipients: Add `victoria.yourdomain.com` (or leave blank for all)
4. Click **Next**
5. Add action: **Deliver to S3 bucket**
   - Bucket: Select your bucket
   - Object key prefix: `emails/`
6. Click **Next** → **Create rule**

## Step 8: Create IAM User for Victoria

1. Go to **AWS Console** → **IAM** → **Users**
2. Click **Create user**
3. User name: `victoria-email-access`
4. Click **Next**
5. Select **Attach policies directly**
6. Search and select: `AmazonS3ReadOnlyAccess`
7. Click **Next** → **Create user**
8. Click on the user → **Security credentials** → **Create access key**
9. Choose **Application running outside AWS**
10. **Save both the Access Key ID and Secret Access Key**

## Step 9: Configure Environment Variables

Add these to your `.env` file:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID="your-access-key-id"
AWS_SECRET_ACCESS_KEY="your-secret-access-key"
AWS_REGION="us-east-2"

# Email S3 Configuration
EMAIL_S3_BUCKET="victoria-email-inbox"
EMAIL_S3_PREFIX="emails/"

# Local storage paths (optional, defaults shown)
EMAIL_ATTACHMENT_DIR="${HOME}/Victoria/email_attachments"
EMAIL_LAST_CHECK_FILE="${HOME}/Victoria/email_last_checked.txt"
```

## Step 10: Test the Setup

1. Send an email to `test@victoria.yourdomain.com`
2. Check your S3 bucket → `emails/` folder
3. You should see a new file (the raw email)
4. Start Victoria and ask her to check her inbox

## MCP Tools Available

Once configured, Victoria has access to these email tools:

| Tool | Description |
|------|-------------|
| `check_inbox` | List new emails since last check |
| `get_email` | Get parsed email details (subject, from, body, attachments) |
| `download_attachment` | Download a specific attachment |
| `download_all_csv_attachments` | Batch download all CSV files |
| `get_inbox_stats` | Get inbox statistics |

## Example Prompts

- "Check your email inbox"
- "Do you have any new emails with CSV attachments?"
- "Download the CSV from the latest daily report email"
- "What emails have you received today?"

## Troubleshooting

### Emails not appearing in S3
- Verify MX record is correct for your region
- Check SES receipt rule is active
- Ensure the rule set is set as active
- Check S3 bucket policy allows SES writes

### Domain not verifying
- DNS propagation can take up to 72 hours
- Verify CNAME records are correctly formatted
- Check for typos in the DNS records

### Victoria can't access emails
- Verify AWS credentials are correct in `.env`
- Check IAM user has `AmazonS3ReadOnlyAccess` policy
- Ensure `EMAIL_S3_BUCKET` matches your actual bucket name

## Cost Estimate

This setup is very cost-effective:
- **SES Email Receiving**: $0.10 per 1,000 emails
- **S3 Storage**: ~$0.023 per GB/month
- **S3 Requests**: $0.0004 per 1,000 GET requests

For a typical use case (100 emails/day with attachments), expect **less than $2/month**.

## Security Considerations

- The IAM user has read-only S3 access (cannot delete or modify emails)
- Using a subdomain isolates Victoria's email from your main domain
- DKIM and DMARC help prevent email spoofing
- S3 bucket is private by default (no public access)
