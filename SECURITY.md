# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.45.x  | :white_check_mark: |
| 3.44.x  | :white_check_mark: |
| < 3.40  | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in IXpansion, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email the maintainers or use GitHub's private vulnerability reporting
3. Include a description of the vulnerability and steps to reproduce
4. You can expect an initial response within 48 hours

## Security Measures

- No credentials are committed to the repository
- API keys are validated at the gateway level
- Rate limiting is enforced on all endpoints
- CORS is configured to allow only necessary origins
- The `.env` file is gitignored and must never be committed
