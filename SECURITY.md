# Security Policy

Thank you for your interest in the security of Community Pulse. We take security seriously and appreciate responsible disclosure of any vulnerabilities.

## Supported Versions

Community Pulse currently maintains the following support matrix:

| Version | Status      | Support |
|---------|-------------|---------|
| 2.x     | Current     | Supported |
| 1.x     | EOL         | Not supported |
| < 1.0   | EOL         | Not supported |

We recommend using the latest 2.x release. Security updates will be provided for the current major version.

## Reporting a Vulnerability

If you discover a security vulnerability in Community Pulse, please report it **privately** to the maintainer:

**Email:** hilliersmmain@gmail.com

**Please include:**
- A description of the vulnerability
- Steps to reproduce the issue (if applicable)
- The affected version(s)
- Any potential impact assessment

**Please do NOT:**
- File a public GitHub issue
- Disclose the vulnerability publicly before we've had time to respond

## Response Timeline

We aim to acknowledge vulnerability reports within **7 days** and will work with you to:
1. Understand the issue
2. Develop a fix
3. Coordinate a responsible disclosure

The exact timeline for a patch depends on the severity and complexity of the issue.

## Security Considerations

Community Pulse is a portfolio project focused on data analytics and quality assessment. It is deployed on Streamlit Cloud with publicly available demo data (synthetic community records). Users should:

- **Not upload sensitive personal data** to the live demo instance
- Use local deployments for handling confidential or private data
- Review dependencies regularly via `pip list` and `pip-audit`

## Dependencies & Updates

We maintain security by:
- Regularly updating dependencies listed in `requirements.txt`
- Running GitHub Actions CI/CD that includes Bandit security scanning
- Using GitHub Dependabot to monitor for vulnerable dependencies

Developers can verify dependency security locally:

```bash
pip install pip-audit
pip-audit
```

---

For general questions or non-security inquiries, please use GitHub Issues.
