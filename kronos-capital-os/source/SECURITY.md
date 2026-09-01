# Security Policy

- Never commit `.env.runtime`, API keys, private keys, bank credentials or bearer tokens.
- Use dedicated trading keys with the minimum venue permissions; disable transfer/withdrawal permission by default.
- Move production secrets from env files to a secrets manager/HSM/KMS-backed system.
- Keep PostgreSQL and Redis private to the deployment network.
- Treat a stale risk/data state as fail-closed for new exposure.
- Rotate compromised credentials immediately and trip the emergency stop before restoring execution.
