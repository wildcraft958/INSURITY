# Aiven Postgres Setup Guide

## Overview
This document outlines the steps to provision and configure Aiven Postgres for the telematics insurance platform.

## 1. Aiven Account Setup

1. Sign up for Aiven account at https://aiven.io
2. Choose your preferred cloud provider (AWS, GCP, Azure, etc.)
3. Select the appropriate region for your application

## 2. Postgres Service Creation

### Service Configuration
- **Service**: PostgreSQL
- **Plan**: Business-4 (recommended for production) or Hobbyist (for development)
- **Cloud**: AWS/GCP/Azure (choose based on your preference)
- **Region**: Choose closest to your application deployment

### Security Settings
- Enable **SSL/TLS encryption** (enabled by default)
- Configure **IP filtering** to allow access from your application servers
- Set up **VPC peering** if using private networks

## 3. Database Schema Setup

After service is provisioned, connect and run the schema creation:

```sql
-- Connect using the provided connection URI
psql "postgres://username:password@host:port/defaultdb?sslmode=require"

-- Create application database
CREATE DATABASE telematics_insurance;

-- Connect to the new database
\c telematics_insurance;

-- Run the table creation scripts from backend/app/services/db.py
-- (The create_tables() method contains all necessary DDL)
```

## 4. Connection Configuration

### Environment Variables
Set these environment variables in your deployment:

```bash
AIVEN_POSTGRES_URI=postgres://username:password@host:port/telematics_insurance?sslmode=require
```

### Connection Pool Settings
- **Min connections**: 1
- **Max connections**: 10
- **Connection timeout**: 60 seconds

## 5. Performance Optimization

### Indexes
The following indexes are automatically created:
- `idx_telematics_driver_timestamp` - For telematics data queries
- `idx_risk_assessments_driver` - For risk assessment lookups
- `idx_policies_driver` - For policy queries
- `idx_claims_policy` - For claims analysis

### Monitoring
- Enable **Performance Insights** in Aiven console
- Set up **alerting** for:
  - High CPU usage (>80%)
  - High connection count (>80% of max)
  - Slow queries (>5 seconds)
  - Storage usage (>80%)

## 6. Backup and Recovery

### Automated Backups
- Aiven provides automatic daily backups
- Point-in-time recovery available for last 7 days
- Configure backup retention period (default: 7 days)

### Manual Backup
```bash
# Create manual backup
pg_dump "postgres://username:password@host:port/telematics_insurance?sslmode=require" > backup.sql

# Restore from backup
psql "postgres://username:password@host:port/telematics_insurance?sslmode=require" < backup.sql
```

## 7. Security Best Practices

### Access Control
1. Create separate database users for different services:
   ```sql
   -- Application user (read/write)
   CREATE USER app_user WITH PASSWORD 'strong_password';
   GRANT CONNECT ON DATABASE telematics_insurance TO app_user;
   GRANT USAGE ON SCHEMA public TO app_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
   
   -- Read-only user for analytics
   CREATE USER analytics_user WITH PASSWORD 'strong_password';
   GRANT CONNECT ON DATABASE telematics_insurance TO analytics_user;
   GRANT USAGE ON SCHEMA public TO analytics_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
   ```

2. Rotate passwords regularly
3. Use connection pooling to manage connections efficiently

### Network Security
- Enable IP allowlisting in Aiven console
- Use VPC peering for production environments
- Always use SSL/TLS connections

## 8. Migration Scripts

### Initial Data Migration
```python
# Python script for migrating existing data
import pandas as pd
import asyncpg
import asyncio

async def migrate_data():
    conn = await asyncpg.connect("your_aiven_connection_string")
    
    # Example: Migrate driver data
    drivers_df = pd.read_csv('existing_drivers.csv')
    
    for _, driver in drivers_df.iterrows():
        await conn.execute("""
            INSERT INTO drivers (email, first_name, last_name, age, gender)
            VALUES ($1, $2, $3, $4, $5)
        """, driver['email'], driver['first_name'], driver['last_name'], 
             driver['age'], driver['gender'])
    
    await conn.close()

# Run migration
asyncio.run(migrate_data())
```

## 9. Monitoring and Alerting

### Key Metrics to Monitor
1. **Connection count**: Should not exceed 80% of max connections
2. **Query performance**: Monitor slow queries (>5s)
3. **Disk usage**: Set alerts at 80% capacity
4. **CPU utilization**: Alert at 80% sustained usage
5. **Memory usage**: Monitor for memory pressure

### Aiven Console Setup
1. Navigate to service overview in Aiven console
2. Configure alerts for critical metrics
3. Set up notification channels (email, Slack, etc.)

## 10. Cost Optimization

### Right-sizing
- Start with Hobbyist plan for development
- Use Business-4 for production with moderate load
- Scale up to Business-8 or higher for high-traffic applications

### Query Optimization
- Regularly review slow query logs
- Optimize indexes based on query patterns
- Use EXPLAIN ANALYZE for query performance analysis

## 11. Troubleshooting

### Common Issues

1. **Connection timeouts**
   - Check IP allowlist settings
   - Verify SSL configuration
   - Monitor connection pool exhaustion

2. **Slow queries**
   - Review and optimize indexes
   - Analyze query execution plans
   - Consider query refactoring

3. **High memory usage**
   - Tune PostgreSQL parameters
   - Optimize large result set queries
   - Consider connection pooling

### Support
- Aiven provides 24/7 support for Business plans
- Community support available for Hobbyist plans
- Documentation: https://aiven.io/docs/products/postgresql

## 12. Production Checklist

- [ ] Service provisioned with appropriate plan
- [ ] SSL/TLS encryption enabled
- [ ] IP allowlist configured
- [ ] Database schema created
- [ ] Indexes created and optimized
- [ ] Backup strategy configured
- [ ] Monitoring and alerting set up
- [ ] Security best practices implemented
- [ ] Performance testing completed
- [ ] Disaster recovery plan documented
