# Code Blocks Test

This document tests code block rendering with different languages.

## Python Code

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

## JavaScript Code

```javascript
function fetchData(url) {
  return fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log('Data received:', data);
      return data;
    })
    .catch(error => {
      console.error('Error:', error);
    });
}
```

## Bash Script

```bash
#!/bin/bash

# Backup script
BACKUP_DIR="/backup"
SOURCE_DIR="/data"

echo "Starting backup..."
tar -czf "${BACKUP_DIR}/backup-$(date +%Y%m%d).tar.gz" "${SOURCE_DIR}"
echo "Backup completed!"
```

## Inline Code

You can also use inline code like `npm install` or `git commit -m "message"` within sentences.

## Code Without Language

```
This is a code block without a specific language.
It should still be formatted as code.
```
