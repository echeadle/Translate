# Complex Markdown Document

This document combines multiple markdown features to test comprehensive PDF rendering.

## Executive Summary

This is a **complex test document** that demonstrates various markdown features working together. It includes:

- Headers at different levels
- Text formatting (*italic*, **bold**, `code`)
- Lists and nested structures
- Code blocks with syntax highlighting
- Tables with data
- Blockquotes and horizontal rules

---

## Code Examples

### Python Data Processing

```python
import pandas as pd
import numpy as np

def process_data(df):
    """Process and clean data."""
    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values
    df = df.fillna(df.mean())

    # Normalize numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()

    return df
```

### SQL Query Example

```sql
SELECT
    users.name,
    COUNT(orders.id) as order_count,
    SUM(orders.total) as revenue
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE orders.created_at >= '2024-01-01'
GROUP BY users.id, users.name
HAVING order_count > 5
ORDER BY revenue DESC
LIMIT 10;
```

## Performance Metrics

| Metric          | Q1 2024 | Q2 2024 | Q3 2024 | Change |
|-----------------|---------|---------|---------|--------|
| Revenue         | $1.2M   | $1.5M   | $1.8M   | +20%   |
| Users           | 10,000  | 12,500  | 15,000  | +20%   |
| Conversion Rate | 2.5%    | 2.8%    | 3.1%    | +11%   |
| Churn Rate      | 5.0%    | 4.5%    | 4.0%    | -11%   |

## Architecture Overview

### System Components

1. **Frontend Layer**
   - React application
   - Redux state management
   - Responsive design with Tailwind CSS

2. **API Layer**
   - RESTful API with Express.js
   - Authentication via JWT
   - Rate limiting and caching

3. **Database Layer**
   - PostgreSQL for relational data
   - Redis for caching
   - MongoDB for logs

### Key Features

- ✓ Real-time updates via WebSockets
- ✓ Comprehensive error handling
- ✓ Automated testing (95% coverage)
- ✓ CI/CD pipeline with GitHub Actions

## Best Practices

> **Important:** Always follow security best practices when handling user data.
>
> - Encrypt sensitive information
> - Use parameterized queries
> - Implement proper authentication
> - Regular security audits

### Configuration Example

```yaml
server:
  port: 3000
  host: localhost

database:
  type: postgres
  host: db.example.com
  port: 5432
  name: production_db

cache:
  type: redis
  host: cache.example.com
  ttl: 3600
```

## Command Reference

Quick reference for common commands:

| Command                  | Description                      |
|--------------------------|----------------------------------|
| `npm install`            | Install dependencies             |
| `npm run dev`            | Start development server         |
| `npm run build`          | Build for production             |
| `npm test`               | Run test suite                   |
| `npm run lint`           | Check code quality               |

## Troubleshooting

### Common Issues

**Problem:** Application won't start

**Solution:** Check that all environment variables are set correctly:

```bash
export DATABASE_URL="postgresql://user:pass@localhost/db"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="your-secret-key"
```

---

**Problem:** Slow query performance

**Solution:** Ensure indexes are created:

```sql
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_at);
```

## Conclusion

This document demonstrates that the markdown-to-PDF converter can handle:

1. Complex nested structures
2. Multiple code languages
3. Tables with varied content
4. Mixed content types
5. Professional formatting

For more information, visit the [documentation](https://example.com/docs).
