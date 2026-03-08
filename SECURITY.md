# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of our project seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Publicly Disclose

Please do not open a public GitHub issue for security vulnerabilities.

### 2. Report Privately

Report security vulnerabilities by:
- Opening a private security advisory on GitHub
- Emailing the maintainers (if contact info is available)
- Creating a private discussion

### 3. Include Details

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information

### 4. Response Time

- We will acknowledge receipt within 48 hours
- We will provide a detailed response within 7 days
- We will work on a fix and keep you updated

## Security Best Practices

### For Users

1. **Keep Software Updated**
   ```bash
   git pull origin main
   pip install --upgrade -r requirements.txt
   ```

2. **Use Latest Ollama Version**
   ```bash
   ollama --version
   # Update if needed
   ```

3. **Validate Input**
   - Don't process untrusted blog content
   - Sanitize user inputs
   - Limit content length

4. **Secure Your Environment**
   - Use virtual environments
   - Don't run as root/admin
   - Keep dependencies updated

5. **Network Security**
   - Run web interface on localhost only
   - Use firewall rules
   - Enable HTTPS in production

### For Developers

1. **Code Review**
   - Review all pull requests
   - Check for security issues
   - Use automated scanning tools

2. **Dependency Management**
   ```bash
   # Check for vulnerabilities
   pip-audit
   
   # Update dependencies
   pip install --upgrade -r requirements.txt
   ```

3. **Input Validation**
   ```python
   from error_handler import validate_input
   
   error = validate_input(content, title)
   if error:
       return {'success': False, 'error': error}
   ```

4. **Secure File Operations**
   ```python
   import os
   from pathlib import Path
   
   # Validate file paths
   safe_path = Path(output_dir) / filename
   if not safe_path.resolve().is_relative_to(Path(output_dir).resolve()):
       raise ValueError("Invalid file path")
   ```

5. **Environment Variables**
   ```python
   # Don't hardcode secrets
   import os
   api_key = os.getenv('API_KEY')
   ```

## Known Security Considerations

### 1. Local AI Processing

**Risk**: Ollama runs locally with system access

**Mitigation**:
- Run in isolated environment
- Use user-level permissions
- Monitor resource usage

### 2. File System Access

**Risk**: Application writes to disk

**Mitigation**:
- Validate all file paths
- Use restricted directories
- Implement file size limits

### 3. Web Interface

**Risk**: Flask development server

**Mitigation**:
- Use production WSGI server (Gunicorn)
- Enable HTTPS
- Implement rate limiting
- Add CSRF protection

### 4. User Input

**Risk**: Malicious content injection

**Mitigation**:
- Validate input length
- Sanitize special characters
- Implement content filtering

### 5. Dependencies

**Risk**: Vulnerable packages

**Mitigation**:
- Regular updates
- Security scanning
- Pin versions in production

## Security Checklist

### Development
- [ ] Input validation implemented
- [ ] Error handling in place
- [ ] Logging configured
- [ ] Dependencies updated
- [ ] Code reviewed

### Deployment
- [ ] Production WSGI server
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Rate limiting active
- [ ] Monitoring enabled

### Maintenance
- [ ] Regular updates
- [ ] Security patches applied
- [ ] Logs reviewed
- [ ] Backups configured
- [ ] Incident response plan

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment sent
3. **Day 3-7**: Investigation and assessment
4. **Day 8-14**: Fix development
5. **Day 15-21**: Testing and validation
6. **Day 22-30**: Release and disclosure

## Security Updates

Security updates will be:
- Released as patch versions
- Documented in CHANGELOG.md
- Announced in GitHub releases
- Tagged with "security" label

## Contact

For security concerns:
- GitHub Security Advisories (preferred)
- GitHub Issues (for non-critical issues)
- Project discussions

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be acknowledged in:
- CHANGELOG.md
- GitHub releases
- Security advisories

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Ollama Security](https://ollama.com/docs/security)

---

**Last Updated**: March 2026
