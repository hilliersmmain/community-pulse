# Security Policy

Thank you for your interest in the security of Community Pulse. We take security seriously and appreciate responsible disclosure of any vulnerabilities.

## Supported Versions

Community Pulse has no tagged releases. Fixes land on the `main` branch, the only supported version:

| Version | Status      | Support |
|---------|-------------|---------|
| `main`  | Current     | Supported |

Use the latest `main`. Older commits do not receive security fixes.

## Reporting a Vulnerability

If you discover a security vulnerability in Community Pulse, please report it **privately** to the maintainer:

**Email:** hilliersmmain@gmail.com

**Please include:**
- A description of the vulnerability
- Steps to reproduce the issue (if applicable)
- The commit you tested (or say it was the live demo)
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

How dependencies and code are kept in check:
- Dependabot **version updates** are configured in `.github/dependabot.yml`: a monthly check that opens pull requests for newer `pip` packages (minor and patch updates grouped into one, at most 5 open) and for GitHub Actions versions (all grouped into one, at most 3 open). These are version bumps, not vulnerability reports.
- Dependabot **security alerts are not enabled** on this repository, so GitHub raises no Dependabot alert for a dependency with a published advisory. Run `pip-audit` (below) for that.
- The pins and floors in `requirements.txt` are raised by hand, from those pull requests or when an advisory affects a floor.
- The CI workflow (`.github/workflows/ci.yml`) runs Bandit twice over `utils/ community_pulse/ components/ app.py verify_setup.py scripts/`: first an advisory run that prints every finding to the CI log and never fails the build, then a gate (`-lll -iii`) that fails the build only on a high-severity, high-confidence finding.

Developers can verify dependency security locally:

```bash
pip install pip-audit
pip-audit
```

---

For general questions or non-security inquiries, please use GitHub Issues.
