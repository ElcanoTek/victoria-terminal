# Complete Guide: Setting Up a Read-Only User in Snowflake with PAT Authentication

This comprehensive guide provides all the necessary steps and SQL scripts to create a secure, read-only user in Snowflake. This is particularly useful for AI agents, reporting tools, or any application that needs read-only access to your data. The guide covers creating the user and role, granting the correct permissions, generating a Programmatic Access Token (PAT) for password-less authentication, and finding your account details for configuration.

---

## Overview

A read-only user in Snowflake has the following characteristics:

- **Cannot modify data**: No INSERT, UPDATE, DELETE, or TRUNCATE operations
- **Cannot create objects**: No ability to create tables, views, schemas, or other database objects
- **Can query data**: Full SELECT access to specified databases and schemas
- **Can use compute resources**: Access to a designated warehouse for running queries
- **Secure authentication**: Uses Programmatic Access Token (PAT) instead of traditional passwords

This setup follows the principle of least privilege, ensuring the user has only the permissions necessary to perform read operations.

---

## Prerequisites

Before you begin, ensure you have:

- **ACCOUNTADMIN** or equivalent privileges in Snowflake
- Access to a Snowflake worksheet or SQL client
- The name of the warehouse you want the user to access
- The name(s) of the database(s) you want to grant read access to

---

## Part 1: Create the User and Role

This script creates a new role with read-only permissions and a new user assigned to that role. Execute the following commands in a Snowflake worksheet.

### Complete Setup Script

Copy and paste this entire script into your Snowflake worksheet. Customize the variables at the top, then execute all commands:

```sql
-- ============================================================================
-- SNOWFLAKE READ-ONLY USER SETUP SCRIPT
-- ============================================================================

-- Use the ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- STEP 1: DEFINE YOUR VARIABLES (CUSTOMIZE THESE)
-- ============================================================================
SET user_name = 'READONLY_USER';           -- Name for the new user
SET role_name = 'READONLY_ROLE';           -- Name for the new role
SET warehouse_name = 'YOUR_WAREHOUSE';     -- Warehouse the user can access
SET database_name = 'YOUR_DATABASE';       -- Database to grant read access to
SET user_password = 'CHANGE_ME_123!';      -- Temporary password (will use PAT instead)

-- ============================================================================
-- STEP 2: CREATE THE ROLE
-- ============================================================================
CREATE OR REPLACE ROLE IDENTIFIER($role_name) 
  COMMENT = 'Read-only access role';

-- ============================================================================
-- STEP 3: GRANT WAREHOUSE ACCESS
-- ============================================================================
-- This allows the role to use the warehouse for running queries
GRANT USAGE ON WAREHOUSE IDENTIFIER($warehouse_name) TO ROLE IDENTIFIER($role_name);

-- ============================================================================
-- STEP 4: GRANT DATABASE ACCESS
-- ============================================================================
-- Grant USAGE on the database
GRANT USAGE ON DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- ============================================================================
-- STEP 5: GRANT SCHEMA ACCESS (ALL SCHEMAS)
-- ============================================================================
-- Grant USAGE on all existing schemas in the database
GRANT USAGE ON ALL SCHEMAS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- Grant USAGE on all future schemas in the database
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- ============================================================================
-- STEP 6: GRANT READ ACCESS TO TABLES AND VIEWS (ALL TABLES)
-- ============================================================================
-- IMPORTANT: These grants apply to ALL tables, not individual tables
-- This ensures the user can query any table in the database

-- Grant SELECT on all existing tables in the database
GRANT SELECT ON ALL TABLES IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- Grant SELECT on all existing views in the database
GRANT SELECT ON ALL VIEWS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- Grant SELECT on all future tables in the database
GRANT SELECT ON FUTURE TABLES IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- Grant SELECT on all future views in the database
GRANT SELECT ON FUTURE VIEWS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);

-- ============================================================================
-- STEP 7: CREATE THE USER
-- ============================================================================
CREATE OR REPLACE USER IDENTIFIER($user_name)
  PASSWORD = $user_password
  DEFAULT_ROLE = $role_name
  COMMENT = 'Read-only user';

-- Grant the role to the user
GRANT ROLE IDENTIFIER($role_name) TO USER IDENTIFIER($user_name);

-- Set the default role for the user
ALTER USER IDENTIFIER($user_name) SET DEFAULT_ROLE = $role_name;

-- ============================================================================
-- STEP 8: VERIFY THE SETUP
-- ============================================================================
-- Check the grants to confirm everything is set up correctly
SHOW GRANTS TO ROLE IDENTIFIER($role_name);
SHOW GRANTS TO USER IDENTIFIER($user_name);

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================
-- Next step: Generate a Programmatic Access Token (see Part 2)
```

---

## Part 2: Generate the Programmatic Access Token (PAT)

A Programmatic Access Token (PAT) is a secure, password-less authentication method. The token acts as a credential that can be used in place of a password when connecting to Snowflake.

### Generate the PAT

Run the following command. **Important: The token will be displayed only once in the output. Copy it immediately and store it securely.**

```sql
-- Generate the Programmatic Access Token (PAT)
-- Customize the token name and expiry days as needed
SET token_name = 'READONLY_PAT';
SET expiry_days = 90;

ALTER USER IDENTIFIER($user_name) ADD PROGRAMMATIC ACCESS TOKEN IDENTIFIER($token_name)
  ROLE_RESTRICTION = $role_name
  DAYS_TO_EXPIRY = $expiry_days
  COMMENT = 'PAT for read-only access';
```

### Understanding the Output

The command will return a result set with two columns:

| Column | Description |
|--------|-------------|
| `token_name` | The name of the token (e.g., READONLY_PAT) |
| `token_secret` | The actual token string - **copy this value!** |

The `token_secret` is what you'll use as the password in your connection configuration. This is the only time you'll be able to see this value.

---

## Part 3: Find Your Snowflake Account Identifier

Your account identifier is required for connecting to Snowflake. There are two ways to find it:

### Method 1: Using SQL

```sql
-- Get your account locator (e.g., xy12345.us-east-1)
SELECT CURRENT_ACCOUNT();

-- Get your organization and account name
SELECT CURRENT_ORGANIZATION_NAME() AS org_name, 
       CURRENT_ACCOUNT_NAME() AS account_name;
-- The full identifier format is: <org_name>-<account_name>
```

### Method 2: Using Snowsight UI

1. Click on your user icon in the top right corner
2. Click on **Account**
3. Copy the account identifier displayed in the dialog

---

## Part 4: Configure Your Application

Now you have all the information needed to configure your application or tool to connect to Snowflake. Here's a typical configuration format:

### Generic Configuration Template

```ini
SNOWFLAKE_ACCOUNT="<your-account-identifier>"    # From Part 3
SNOWFLAKE_USER="<your-user-name>"                # From Part 1 (e.g., READONLY_USER)
SNOWFLAKE_PASSWORD="<your-pat-token>"            # The token_secret from Part 2
SNOWFLAKE_WAREHOUSE="<your-warehouse-name>"      # From Part 1
SNOWFLAKE_DATABASE="<your-database-name>"        # From Part 1
SNOWFLAKE_SCHEMA="<your-schema-name>"            # Optional: default schema
```

### Example Python Connection

```python
import snowflake.connector

conn = snowflake.connector.connect(
    user='READONLY_USER',
    password='<your-pat-token>',  # Use the PAT token here
    account='xy12345.us-east-1',
    warehouse='YOUR_WAREHOUSE',
    database='YOUR_DATABASE',
    schema='PUBLIC'
)
```

---

## Important: Handling Case-Sensitive Table Names

Snowflake table and column names can be case-sensitive if they were created with quotes. This is a common issue that can prevent queries from working.

### Understanding Case Sensitivity

When you create a table in Snowflake:

**Without quotes** (case-insensitive, converted to uppercase):
```sql
CREATE TABLE my_table (id INT);  -- Stored as MY_TABLE
```

**With quotes** (case-sensitive, preserves exact case):
```sql
CREATE TABLE "My_Table" (id INT);  -- Stored as My_Table
```

### Querying Case-Sensitive Tables

If your tables were created with quotes (case-sensitive names), you **must** use quotes when querying them:

```sql
-- WRONG - Will fail if table name is case-sensitive
SELECT * FROM My_Table;

-- CORRECT - Use quotes to preserve case
SELECT * FROM "My_Table";

-- CORRECT - Fully qualified with quotes
SELECT * FROM "DATABASE_NAME"."SCHEMA_NAME"."My_Table";
```

### For AI Agents and Applications

When using AI agents or programmatic access, ensure your queries use proper quoting. You can discover the exact table names (with correct casing) using:

```sql
-- This returns the exact table names as they are stored
SELECT table_name 
FROM INFORMATION_SCHEMA.TABLES 
WHERE table_schema = 'YOUR_SCHEMA'
ORDER BY table_name;
```

Then use those exact names with quotes in your queries.

---

## Discovering Available Data

Since `SHOW` commands may be restricted by some MCP configurations, use `INFORMATION_SCHEMA` queries instead. These are standard SQL SELECT queries that work with read-only permissions.

### List All Accessible Tables

```sql
-- List all tables you have access to
SELECT 
    table_catalog AS database_name,
    table_schema AS schema_name,
    table_name,
    table_type
FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema != 'INFORMATION_SCHEMA'
ORDER BY table_schema, table_name;
```

### List Tables in a Specific Schema

```sql
-- List tables in a specific schema
SELECT table_name, table_type
FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'YOUR_SCHEMA'
ORDER BY table_name;
```

### Get Table Details with Row Counts

```sql
-- Get table details including approximate row counts
SELECT 
    table_name,
    table_type,
    row_count,
    bytes
FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'YOUR_SCHEMA'
ORDER BY table_name;
```

### View Table Structure (Columns)

```sql
-- See all columns in all accessible tables
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type,
    is_nullable
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_schema = 'YOUR_SCHEMA'
ORDER BY table_schema, table_name, ordinal_position;
```

### List Available Schemas

```sql
-- List all schemas in the database
SELECT schema_name
FROM INFORMATION_SCHEMA.SCHEMATA
ORDER BY schema_name;
```

---

## Advanced Configuration

### Granting Access to Multiple Databases

If you need to grant read access to multiple databases, repeat the grant statements for each database:

```sql
-- For each additional database
SET database_name = 'ANOTHER_DATABASE';

GRANT USAGE ON DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT USAGE ON ALL SCHEMAS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON ALL TABLES IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON ALL VIEWS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON FUTURE TABLES IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON FUTURE VIEWS IN DATABASE IDENTIFIER($database_name) TO ROLE IDENTIFIER($role_name);
```

### Granting Access to Specific Schemas Only

If you want to limit access to specific schemas rather than all schemas in a database:

```sql
-- Grant USAGE on specific schemas
GRANT USAGE ON SCHEMA YOUR_DATABASE.SCHEMA_1 TO ROLE IDENTIFIER($role_name);
GRANT USAGE ON SCHEMA YOUR_DATABASE.SCHEMA_2 TO ROLE IDENTIFIER($role_name);

-- Grant SELECT on tables in specific schemas
GRANT SELECT ON ALL TABLES IN SCHEMA YOUR_DATABASE.SCHEMA_1 TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON ALL VIEWS IN SCHEMA YOUR_DATABASE.SCHEMA_1 TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON FUTURE TABLES IN SCHEMA YOUR_DATABASE.SCHEMA_1 TO ROLE IDENTIFIER($role_name);
GRANT SELECT ON FUTURE VIEWS IN SCHEMA YOUR_DATABASE.SCHEMA_1 TO ROLE IDENTIFIER($role_name);
```

---

## Managing Programmatic Access Tokens

### List All PATs for a User

```sql
-- View all programmatic access tokens for a user
SHOW USER PROGRAMMATIC ACCESS TOKENS FOR IDENTIFIER($user_name);
```

### Remove a PAT

If you need to revoke or regenerate a token:

```sql
-- Remove an existing PAT
ALTER USER IDENTIFIER($user_name) REMOVE PROGRAMMATIC ACCESS TOKEN IDENTIFIER($token_name);
```

### Rotate a PAT

To rotate a token (create a new one before removing the old one):

```sql
-- Create a new token with a different name
ALTER USER IDENTIFIER($user_name) ADD PROGRAMMATIC ACCESS TOKEN NEW_READONLY_PAT
  ROLE_RESTRICTION = $role_name
  DAYS_TO_EXPIRY = 90
  COMMENT = 'Rotated PAT for read-only access';

-- After updating your applications with the new token, remove the old one
ALTER USER IDENTIFIER($user_name) REMOVE PROGRAMMATIC ACCESS TOKEN IDENTIFIER($token_name);
```

---

## Security Best Practices

When implementing read-only access in Snowflake, consider the following security recommendations:

**Use PAT tokens instead of passwords.** Programmatic Access Tokens provide better security than traditional passwords and are designed for automated systems and applications. They can be easily rotated and revoked without changing the user's password.

**Set appropriate token expiration.** Configure token expiration based on your security policies. The default is 15 days, with a maximum of 365 days. For production systems, consider using shorter expiration periods (30-90 days) and implementing a token rotation process.

**Apply the principle of least privilege.** Only grant access to the specific databases and schemas that the user needs. Avoid granting access to all databases unless absolutely necessary. Use the `GRANT SELECT ON ALL TABLES IN DATABASE` syntax to ensure comprehensive access within the specified scope.

**Monitor usage regularly.** Use Snowflake's query history and access logs to monitor the read-only user's activity. Set up alerts for unusual query patterns or excessive resource consumption.

**Implement network policies.** By default, Snowflake requires users with PAT tokens to be subject to a network policy. This restricts access to specific IP addresses or ranges, adding an additional layer of security.

**Store tokens securely.** Treat PAT tokens like passwords. Store them in secure credential management systems or environment variables, never in source code or configuration files committed to version control.

**Use role restrictions.** When creating PAT tokens, always specify the `ROLE_RESTRICTION` parameter to limit the token to a specific role. This ensures that even if the token is compromised, it can only be used with the intended permissions.

**Grant on ALL tables, not individual tables.** Always use `GRANT SELECT ON ALL TABLES IN DATABASE` rather than granting on individual tables. This ensures consistent access and prevents issues where some tables are accessible and others are not.

---

## Troubleshooting

### Common Issues and Solutions

**Issue: "Object does not exist or not authorized"**

This usually means one of the following:

1. **Missing grants on ALL tables**: You granted SELECT on individual tables instead of ALL tables. Run:
   ```sql
   GRANT SELECT ON ALL TABLES IN DATABASE your_database TO ROLE your_role;
   ```

2. **Case-sensitive table names**: The table was created with quotes. Use quotes in your query:
   ```sql
   SELECT * FROM "Exact_Table_Name";
   ```

3. **Missing USAGE on database or schema**: Ensure you have:
   ```sql
   GRANT USAGE ON DATABASE your_database TO ROLE your_role;
   GRANT USAGE ON ALL SCHEMAS IN DATABASE your_database TO ROLE your_role;
   ```

**Issue: "Statement type of Command is not allowed"**

This is an MCP configuration issue, not a Snowflake permissions issue. The MCP server is blocking `SHOW` commands. Use `INFORMATION_SCHEMA` queries instead:

```sql
-- Instead of: SHOW TABLES;
-- Use:
SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'YOUR_SCHEMA';
```

**Issue: "SQL compilation error: syntax error"**

- Ensure all variable names match exactly (case-sensitive)
- Verify that warehouse, database, and schema names exist
- Check that you're using `IDENTIFIER($variable_name)` for dynamic object names
- Verify token names are NOT in quotes when creating PATs

**Issue: "Network policy requirement not met"**

- By default, PAT tokens require a network policy
- Create a network policy and assign it to the user, or
- Modify the authentication policy to bypass this requirement (not recommended for production)

**Issue: "Insufficient privileges to operate on database"**

- Ensure you're running the script with `ACCOUNTADMIN` or equivalent role
- Verify that the database exists and you have privileges on it

**Issue: "Token not working for authentication"**

- Verify you copied the entire `token_secret` value
- Check that the token hasn't expired
- Ensure the role restriction matches the user's granted roles
- Confirm the user is subject to a network policy if required

---

## Verification Checklist

After completing the setup, verify that everything is configured correctly by running these commands as ACCOUNTADMIN:

```sql
-- 1. Verify the role was created
SHOW ROLES LIKE 'READONLY_ROLE';

-- 2. Verify the user was created
SHOW USERS LIKE 'READONLY_USER';

-- 3. Verify grants to the role (should include ALL TABLES grants)
SHOW GRANTS TO ROLE IDENTIFIER($role_name);

-- 4. Verify grants to the user
SHOW GRANTS TO USER IDENTIFIER($user_name);

-- 5. Verify PAT tokens for the user
SHOW USER PROGRAMMATIC ACCESS TOKENS FOR IDENTIFIER($user_name);
```

### What to Look For

In the grants output, you should see:

- ✅ `USAGE` on the warehouse
- ✅ `USAGE` on the database
- ✅ `USAGE` on ALL SCHEMAS in the database (or specific schemas)
- ✅ `SELECT` on ALL TABLES in the database (not individual tables)
- ✅ `SELECT` on ALL VIEWS in the database
- ✅ Future grants for SCHEMAS, TABLES, and VIEWS

---

## Summary

By following this guide, you have successfully created a secure, read-only user in Snowflake with the following capabilities:

- **Query access** to all tables and views in specified databases and schemas
- **Warehouse usage** for executing queries
- **PAT-based authentication** for enhanced security
- **No data modification** capabilities
- **Automatic access** to future tables and views created in the database

This setup is ideal for analytics tools, reporting applications, AI agents, and any system that needs to read data from Snowflake without the ability to modify it.

### Key Takeaways

1. **Always grant on ALL TABLES**, not individual tables, to ensure comprehensive access
2. **Use INFORMATION_SCHEMA** queries instead of SHOW commands for metadata discovery
3. **Handle case-sensitive table names** properly by using quotes when needed
4. **Use PAT tokens** for secure, password-less authentication
5. **Include FUTURE grants** to automatically provide access to newly created objects

---

**Author:** Manus AI  
**Last Updated:** November 2025  
**Snowflake Documentation References:**
- [Using Programmatic Access Tokens](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens)
- [Configuring Access Control](https://docs.snowflake.com/en/user-guide/security-access-control-configure)
- [GRANT Privileges](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege)
- [INFORMATION_SCHEMA Views](https://docs.snowflake.com/en/sql-reference/info-schema)
