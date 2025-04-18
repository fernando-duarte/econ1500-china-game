# Security Policy

## Supported Versions

Only the latest version of the China Growth Game is currently supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to the project maintainers. All security vulnerabilities will be promptly addressed.

Please include the following information in your report:

- Type of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Best Practices

### Authentication and Authorization

- API key-based authentication is implemented for all endpoints
- Role-based access control ensures users can only access appropriate resources
- Team-specific API keys are generated securely using cryptographically strong random functions
- Admin API keys are stored securely and rotated regularly

### Input Validation and Sanitization

- All API inputs are validated using Pydantic models with strict type checking
- User-provided strings are sanitized to prevent XSS attacks
- Regular expressions are used to filter out potentially harmful characters
- Length limits are enforced on all user inputs

### Network Security

- CORS is configured to allow only specific origins
- Rate limiting protects against brute force and DoS attacks
- Security headers are set to prevent common web vulnerabilities
- All communications should use HTTPS in production

### Container Security

- Docker containers run as non-root users
- Health checks ensure containers are functioning properly
- Minimal base images reduce attack surface
- No unnecessary ports are exposed

### Error Handling

- Detailed error information is logged server-side but not exposed to clients
- Generic error messages are returned to prevent information leakage
- All errors follow a consistent format for easier monitoring

### Dependency Management

- Exact version pinning ensures consistent builds
- Dependencies are regularly updated to incorporate security patches
- Dependency lockfiles prevent unexpected updates
- Automated vulnerability scanning is performed regularly

### Secrets Management

- Sensitive configuration is stored in environment variables
- Production secrets are managed using a secure secrets manager
- No secrets are committed to the repository
- Secrets are rotated regularly

## Security Checklist for Deployment

- [ ] All default passwords have been changed
- [ ] Debug mode is disabled in production
- [ ] HTTPS is properly configured
- [ ] Rate limiting is enabled
- [ ] CORS is properly configured
- [ ] API keys have been generated securely
- [ ] Logging is configured to capture security events
- [ ] Backups are configured and tested
- [ ] Monitoring is in place for suspicious activity
- [ ] All unnecessary services and ports are disabled
