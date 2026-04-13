# Backend Security — Online Form

> Documentation of implemented security measures.
> Update this document on every security change, addition, or configuration update.
> Last updated: 2026-04-13

## 1. Authentication

### Password hashing
- **Algorithm**: bcrypt (via `passlib`)
- **Salting**: Automatic (built into bcrypt)
- **Minimum length**: 8 characters (enforced in `manage_admin.py`)

### JWT tokens
- **Algorithm**: HS256
- **Validity**: 24 hours (`TOKEN_EXPIRE_HOURS` in `auth.py`)
- **Client-side storage**: `localStorage` (to be migrated to HttpOnly cookie — see "Planned improvements")
- **Secret**: `SECRET_KEY` in `.env` (not versioned, permissions 600)

## 2. Rate Limiting

### Application-level rate limiting (slowapi)

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/api/login` | 5 per 5 minutes | Brute force protection |
| `/api/responses` | 3 per hour | Anti-spam on form submissions |
| `/api/export/csv` | 10 per hour | Prevent export overload |
| `/api/export/excel` | 10 per hour | Prevent export overload |

- **Library**: `slowapi` (based on `limits`)
- **Identification**: By source IP (`get_remote_address`)
- **Response on exceeded**: HTTP 429, `{"detail": "rate_limited"}`
- **Frontend**: Translated messages (fr/en) via `login.rate_limited` and `form.rate_limited`
- **Logging**: WARNING with IP and path

### How it works
1. `slowapi` maintains an in-memory counter per IP per endpoint
2. On each request, the counter is incremented
3. If the counter exceeds the limit within the time window → HTTP 429 rejection
4. The counter resets automatically after the time window expires
5. In-memory storage: resets on server restart

### Known limitations
- In-memory storage (not persistent across restarts)
- An attacker with multiple IPs (botnet) can bypass the per-IP limit
- No per-account lockout (see "Planned improvements")
- Does not protect against volumetric DoS (see Traefik rate limiting — to be added)

## 3. Data Validation

### Form submissions
- **Validation**: Pydantic (strict schemas in `main.py`)
- **Types**: Enums for gender, status, language
- **Likert scale**: Integers 1-5 (`Field(ge=1, le=5)`)
- **Comment**: Free text, optional (to be limited — see "Planned improvements")

### Login
- **Form**: `OAuth2PasswordRequestForm` (FastAPI standard)
- **SQL injection**: Protected by SQLAlchemy ORM (parameterized queries)

## 4. Network Security

### Firewall (ufw)
- **Open ports**: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- **Port 8000**: Restricted to Docker networks (172.17.0.0/16, 172.18.0.0/16)
- **Default policy**: deny incoming, allow outgoing, allow routed

### HTTPS
- **Certificates**: Let's Encrypt via Traefik (automatic)
- **HTTP→HTTPS redirect**: Automatic (Traefik entrypoint web → websecure)

## 5. Security Logging

### Logged events
| Event | Level | Format |
|-------|-------|--------|
| Successful login | INFO | `Admin login success: user=X, ip=Y` |
| Failed login | WARNING | `Admin login failed: user=X, ip=Y` |
| Rate limit exceeded | WARNING | `Rate limit exceeded: ip=X, path=Y` |
| Form submission | INFO | `Form submission received: id=X, lang=Y, status=Z` |
| Submission error | ERROR | `Form submission failed: ...` |
| CSV/Excel export | INFO | `Export performed: type=X, by=Y, rows=Z` |
| Admin operation | INFO | `Admin created/deleted/password changed: user=X` |

### Viewing logs
```bash
sudo journalctl -u online-form -f                           # Real-time
sudo journalctl -u online-form | grep "Admin login failed"  # Failed logins
sudo journalctl -u online-form | grep "Rate limit"          # Rate limit events
sudo journalctl -u online-form | grep "ERROR"               # Errors
```

## 6. Secrets and Sensitive Files

| File | Content | Protection |
|------|---------|------------|
| `backend/.env` | SECRET_KEY, LOG_LEVEL | .gitignore + chmod 600 |
| `backend/responses.db` | Survey data | .gitignore, app access only |
| `~/.ssh/id_deploy_online_form` | GitHub deploy key | Read-only, VPS only |

## 7. Respondent Anonymity

- **No IP collection** in form submissions
- **No personal identifiers** collected
- **No cookies** for respondents
- Submission logs only contain: id, language, status (respondent category)

## 8. Planned Improvements

| # | Measure | Priority | Status |
|---|---------|----------|--------|
| 1 | ~~Rate limiting on `/api/responses`~~ | High | Done |
| 2 | HTTP security headers (CSP, HSTS, X-Frame-Options) | High | To do |
| 3 | `.env` permissions chmod 600 | High | To verify on VPS |
| 4 | Limit comment field length (max_length) | Medium | To do |
| 5 | JWT token in HttpOnly cookie | Medium | To do |
| 6 | Reduce JWT validity (24h → 4h) | Medium | To do |
| 7 | Account lockout after N failed attempts | Medium | To do |
| 8 | Fail2ban (system-level IP blocking) | Medium | To do |
| 9 | Automatic database backup | Medium | To do |
