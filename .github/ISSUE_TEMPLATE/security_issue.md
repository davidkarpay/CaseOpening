---
name: Security Issue
about: Report a security vulnerability (PRIVATE - only visible to maintainers)
title: '[SECURITY] '
labels: ['security', 'critical']
assignees: ['davidkarpay']

---

## ⚠️ SECURITY NOTICE
**Please do NOT create a public issue for security vulnerabilities.**

If this is a security vulnerability, please report it privately by:
1. Emailing dkarpay@pd15.org with subject line "SECURITY: Case Opening Manager"
2. Using GitHub's private vulnerability reporting (if available)

---

## Security Issue Type
- [ ] Authentication bypass
- [ ] Data exposure (case information)
- [ ] Code injection
- [ ] Cross-site scripting (XSS)
- [ ] SQL injection
- [ ] File system access
- [ ] Privilege escalation
- [ ] Dependency vulnerability
- [ ] Configuration issue
- [ ] Other: ___________

## Severity Level
- [ ] Critical - Immediate threat to case data confidentiality
- [ ] High - Significant security risk
- [ ] Medium - Moderate security concern
- [ ] Low - Minor security improvement

## Affected Components
- [ ] Authentication system
- [ ] Case database
- [ ] PDF generation
- [ ] File uploads/downloads
- [ ] Session management
- [ ] User interface
- [ ] Dependencies
- [ ] Configuration

## Environment
**Where was this discovered?**
- [ ] Local development environment
- [ ] Streamlit Cloud deployment
- [ ] Production environment
- [ ] Testing environment

## Discovery Method
- [ ] Manual testing
- [ ] Automated security scan
- [ ] Code review
- [ ] User report
- [ ] Penetration testing
- [ ] Other: ___________

## Detailed Description
**Please describe the security issue:**
(Use general terms, avoid specific exploit details in public issues)

## Impact Assessment
**What could an attacker potentially do?**
- [ ] Access unauthorized case data
- [ ] Modify case information
- [ ] Bypass authentication
- [ ] Execute arbitrary code
- [ ] Access system files
- [ ] Escalate privileges
- [ ] Other: ___________

**How many users could be affected?**
- [ ] Single user
- [ ] Multiple users
- [ ] All users
- [ ] Depends on configuration

## Reproducibility
- [ ] Always reproducible
- [ ] Sometimes reproducible
- [ ] Difficult to reproduce
- [ ] One-time occurrence

## Mitigation
**Are there any temporary mitigations or workarounds?**

## Additional Information
**Any additional context that might help address this issue:**

---

## For Maintainer Use Only

### Verification Status
- [ ] Vulnerability confirmed
- [ ] Unable to reproduce
- [ ] Not a security issue
- [ ] Duplicate of existing issue

### Response Timeline
- **Acknowledged:** ___________
- **Initial Assessment:** ___________
- **Fix Developed:** ___________
- **Testing Complete:** ___________
- **Deployed:** ___________

### CVE Information
- **CVE ID:** ___________
- **CVSS Score:** ___________

### Public Disclosure
- **Disclosure Date:** ___________
- **Security Advisory:** ___________