# Security notes

This is a development/reference implementation, not a certified production legal-data system.

Implemented:
- password hashing
- JWT authentication
- role checks
- user-scoped OCR access
- audit logging for key actions

Before production:
- replace demo credentials
- use a strong secret from a secret manager
- enforce HTTPS
- use secure cookie/session strategy if browser-token architecture is changed
- encrypt storage and backups
- scan uploads for malware
- restrict file types/content sizes
- configure retention/deletion
- add MFA/SSO where required
- perform an authorization review for every endpoint
- implement granular sensitive-case visibility groups
- avoid putting real client confidential information into development/demo databases
