# RedTeam Playground

**RedTeam Playground** (repo: `redt6eamplaground`) is an intentionally vulnerable web application designed for hands-on red team exercises, penetration testing practice, and exploit research. The project includes a curated set of common web vulnerabilities—such as SQL Injection, Cross-Site Scripting (XSS), CSRF, insecure file uploads, broken authentication, and more—each documented with reproducible PoCs and remediation steps.

This repository is strictly for educational and authorized testing purposes. Do **not** deploy RedTeam Playground on public or production infrastructure.

## What you’ll find
- Guided labs covering OWASP Top 10 vulnerabilities
- Reproducible proof-of-concepts in `/pocs/`
- Patch examples and secure fixes in `/patches/`
- Docker + docker-compose for one-command local deployment
- Issue templates, SECURITY and DISCLAIMER files for safe testing

## Quick start
1. Clone the repo: `https://github.com/Henr1234/RedTeam-Playground.git`
2. run - python3 app.py
3. visit `http://localhost:5000` 

## Responsible usage
Only run this project in isolated/local environments (VMs, Docker, private labs). See `SECURITY.md` and `DISCLAIMER.md` for responsible testing and reporting guidelines.
