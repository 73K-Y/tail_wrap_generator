# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x (Blender 5.0+) | ✅ |
| < 1.0 | ❌ |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately via one of these methods:

- **GitHub Private Advisory**: [Security > Advisories > Report a vulnerability](../../security/advisories/new)
- **Email**: raffaelprivate@gmail.com — subject line `[SECURITY] tail_wrap_generator`

### What to include

- Description of the vulnerability and potential impact
- Steps to reproduce (Blender version, OS, add-on version)
- Any proof-of-concept code if applicable

### Response timeline

| Step | Time |
|---|---|
| Acknowledgement | Within 48 hours |
| Initial assessment | Within 7 days |
| Fix or mitigation | Within 30 days |

You will be credited in the release notes unless you prefer to remain anonymous.

## Scope

This add-on runs entirely inside Blender's Python sandbox with no network access and no external dependencies. Attack surface is limited to:

- Malicious `.blend` files passed as target mesh
- Arbitrary code execution via Blender's scripting environment (out of scope — Blender's responsibility)

## Out of Scope

- Vulnerabilities in Blender itself
- Issues in Python standard library
- Social engineering attacks
