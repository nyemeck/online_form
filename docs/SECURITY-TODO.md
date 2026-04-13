# Security — Remaining Tasks

> Dedicated backlog for security improvements.
> Update this file as tasks are completed or new ones are identified.
> Last updated: 2026-04-14

## Priority Overview

| # | Task | Priority | Effort | Status |
|---|------|----------|--------|--------|
| 1 | HTTP security headers (CSP, HSTS, X-Frame-Options) | High | 20 min | To do |
| 2 | Verify `.env` permissions (chmod 600) | High | 1 min | To verify |
| 3 | Limit comment field length (max_length=5000) | Medium | 1 min | To do |
| 4 | JWT token in HttpOnly cookie | Medium | 1-2h | To do |
| 5 | Reduce JWT validity (24h → 4h) | Medium | 1 min | To do |
| 6 | Account lockout after N failed attempts | Medium | 30 min | To do |
| 7 | Fail2ban (system-level IP blocking) | Medium | 30 min | To do |
| 8 | Automatic database backup | Medium | 20 min | To do |
| 9 | Cloudflare as frontend proxy (optional) | Low | 30 min | To do |

---

## 1. HTTP Security Headers

**Priority**: High
**Effort**: 20 min

### Description
Add security headers to all HTTP responses. Protects against XSS, clickjacking,
MIME sniffing, and protocol downgrade attacks.

### Headers to add
| Header | Value | Protection |
|--------|-------|------------|
| `X-Frame-Options` | `DENY` | Clickjacking |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Protocol downgrade |
| `Content-Security-Policy` | `default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:` | XSS |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Privacy |
| `X-XSS-Protection` | `1; mode=block` | Legacy XSS filter |

### Implementation
Via Traefik middleware in `/root/traefik-config/online-form.yml` (consistent with n8n config).

---

## 2. Verify `.env` Permissions

**Priority**: High
**Effort**: 1 min

### Description
Ensure the `.env` file containing `SECRET_KEY` is only readable by the owner.

### Commands
```bash
ls -l /srv/online_form/backend/.env
# Should be: -rw------- (600) owned by elzouave

# If not:
chmod 600 /srv/online_form/backend/.env
```

---

## 3. Limit Comment Field Length

**Priority**: Medium
**Effort**: 1 min

### Description
The `comment` field in the form has no length limit. An attacker could send megabytes
of text, filling up the database and disk.

### Implementation
In `backend/main.py`, change:
```python
comment: Optional[str] = None
```
to:
```python
comment: Optional[str] = Field(None, max_length=5000)
```

Pydantic will automatically reject submissions with comments > 5000 characters (HTTP 422).

---

## 4. JWT Token in HttpOnly Cookie

**Priority**: Medium
**Effort**: 1-2h

### Description
Currently the JWT token is stored in `localStorage`, which is accessible via JavaScript.
If an XSS vulnerability exists, an attacker can steal the token.

### Implementation overview
- **Backend**: Return token via `Set-Cookie` with `HttpOnly`, `Secure`, `SameSite=Strict`
- **Backend**: Read token from cookie in `get_current_admin()` instead of Authorization header
- **Backend**: Add `/api/logout` endpoint to clear the cookie
- **Frontend**: Remove `localStorage.setItem("admin_token", ...)` from login.html
- **Frontend**: Remove `Authorization` header from dashboard.js fetch calls
- **Frontend**: Update logout to call `/api/logout` endpoint

### Files to modify
- `backend/main.py` (login endpoint, cookie response)
- `backend/auth.py` (read token from cookie)
- `frontend/login.html` (remove localStorage usage)
- `frontend/js/dashboard.js` (remove Authorization header, update logout)

---

## 5. Reduce JWT Validity

**Priority**: Medium
**Effort**: 1 min

### Description
Current JWT validity is 24 hours. If a token is stolen, the attacker has a full day.
Reducing to 4 hours limits the exposure window.

### Implementation
In `backend/auth.py`, change:
```python
TOKEN_EXPIRE_HOURS = 24
```
to:
```python
TOKEN_EXPIRE_HOURS = 4
```

### Note
Best combined with task #4 (HttpOnly cookie) to avoid forcing users to re-login too often.
Consider implementing refresh tokens for a better UX.

---

## 6. Account Lockout After N Failed Attempts

**Priority**: Medium
**Effort**: 30 min

### Description
Rate limiting is per-IP. An attacker using a botnet (many IPs) can bypass it.
Account lockout blocks login attempts for a specific username regardless of IP.

### Implementation options
- **Option A**: In-memory counter (simple, lost on restart)
- **Option B**: Database column `locked_until` on `admins` table (persistent)

### Logic
1. On failed login: increment counter for username
2. If counter > 5 in 15 minutes: reject all login attempts for that username
3. After 15 minutes: counter resets automatically

### Risk
An attacker could intentionally lock out admin accounts (DoS on admins).
Mitigation: use CAPTCHA after N failures instead of hard lockout.

---

## 7. Fail2ban

**Priority**: Medium
**Effort**: 30 min

### Description
System-level tool that monitors logs and automatically bans IPs via firewall rules.
More effective than application-level blocking because it operates at the network layer.

### Implementation
1. Install: `sudo apt install fail2ban`
2. Create filter: `/etc/fail2ban/filter.d/online-form-login.conf`
   - Regex: `Admin login failed: user=.*, ip=<HOST>`
3. Create jail in `/etc/fail2ban/jail.local`:
   - `maxretry = 5`, `bantime = 1h`, `findtime = 10m`
4. Restart: `sudo systemctl restart fail2ban`

### Dependency
Requires the logging system to output to journald (already in place).

---

## 8. Automatic Database Backup

**Priority**: Medium
**Effort**: 20 min

### Description
SQLite is a single file (`responses.db`). If it gets corrupted, deleted, or the disk
fails, all research data is lost.

### Implementation
1. Create backup script: `/srv/online_form/scripts/backup.sh`
   - Copy `responses.db` with timestamp
   - Retain last 30 backups, delete older ones
2. Add cron job: `0 3 * * *` (daily at 3 AM)
3. Optionally sync to external storage (S3, other VPS)

---

## 9. Cloudflare as Frontend Proxy (Optional)

**Priority**: Low
**Effort**: 30 min

### Description
Cloudflare sits between users and the VPS, providing DDoS protection, CDN caching,
and a Web Application Firewall (WAF) — all on the free tier.

### Implementation
1. Create Cloudflare account (free)
2. Add domain `srv1163941.hstgr.cloud`
3. Update DNS nameservers at Hostinger to point to Cloudflare
4. Cloudflare proxies traffic to VPS

### Trade-off
Cloudflare terminates HTTPS and re-encrypts to the VPS. They can see the traffic content.
For an academic survey, this is acceptable.

---

## Completed Tasks

| Task | Date | Commit |
|------|------|--------|
| Rate limiting on `/api/login` (5/5min) | 2026-04-14 | `31bd83d` |
| Rate limiting on `/api/responses` (3/h) | 2026-04-14 | `31bd83d` |
| Rate limiting on exports (10/h) | 2026-04-14 | `31bd83d` |
| Traefik global rate limiting (50 req/s) | 2026-04-14 | `7634416` |
| Centralized logging system | 2026-04-09 | `30d90d2` |
| Firewall (ufw) configuration | 2026-04-08 | `7797ef8` |
| bcrypt password hashing | Initial | — |
| HTTPS via Traefik/Let's Encrypt | 2026-04-08 | — |
