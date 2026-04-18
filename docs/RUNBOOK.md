# Runbook — online-form

> Guide des procedures operationnelles pour les services sur le VPS.
> Derniere mise a jour : 2026-04-08

## 0. Developpement local (Mac)

### Lancer le serveur FastAPI en local

```bash
cd /Users/nyemeck/Projects/backend_projects/online_form
source venv/bin/activate
cd backend
uvicorn main:app --reload
```

L'option `--reload` redemarre automatiquement le serveur quand un fichier change.

### Acceder a l'application en local

| URL                                | Page                          |
|------------------------------------|-------------------------------|
| http://localhost:8000              | Formulaire public             |
| http://localhost:8000/login        | Page de connexion admin       |
| http://localhost:8000/dashboard    | Tableau de bord (apres login) |

### Arreter le serveur local

`Ctrl+C` dans le terminal ou est lance uvicorn.

---

## 1. Service FastAPI (Systemd)

Fichier de service : `/etc/systemd/system/online-form.service`

### Demarrer le service
```bash
sudo systemctl start online-form
```

### Arreter le service
```bash
sudo systemctl stop online-form
```

### Redemarrer le service
```bash
sudo systemctl restart online-form
```

### Voir le statut du service
```bash
sudo systemctl status online-form
```

### Voir les logs en temps reel
```bash
sudo journalctl -u online-form -f
```

### Voir les 50 dernieres lignes de logs
```bash
sudo journalctl -u online-form -n 50
```

### Filtrer les logs applicatifs

Le format des logs est : `timestamp | NIVEAU | logger | message`.

```bash
# Toutes les soumissions de formulaires
sudo journalctl -u online-form | grep "Form submission"

# Toutes les tentatives de login
sudo journalctl -u online-form | grep "Admin login"

# Uniquement les connexions echouees
sudo journalctl -u online-form | grep "Admin login failed"

# Tous les exports
sudo journalctl -u online-form | grep "Export performed"

# Erreurs uniquement
sudo journalctl -u online-form | grep "ERROR"

# Logs de la derniere heure
sudo journalctl -u online-form --since "1 hour ago"
```

### Changer le niveau de logs (DEBUG, INFO, WARNING, ERROR)

```bash
# Editer le .env
sudo nano /srv/online_form/backend/.env
# → modifier LOG_LEVEL=DEBUG (par exemple)

# Redemarrer pour appliquer
sudo systemctl restart online-form
```

### Tester que l'application repond (en local)
```bash
curl http://127.0.0.1:8000
```

### Tester que l'application repond (via Traefik)
```bash
curl -k https://form.srv1163941.hstgr.cloud
```

### Activer / Desactiver le demarrage automatique
```bash
# Activer (demarre au boot du serveur)
sudo systemctl enable online-form

# Desactiver (ne demarre plus au boot)
sudo systemctl disable online-form
```

### Apres modification du fichier de service
```bash
sudo systemctl daemon-reload && sudo systemctl restart online-form
```

## 2. Services Docker (Traefik + n8n)

Fichier Compose : `/root/docker-compose.yml`

### Voir les conteneurs actifs
```bash
sudo docker ps
```

### Redemarrer tous les services Docker
```bash
sudo bash -c "cd /root && docker compose down && docker compose up -d"
```
> **Note** : On utilise `sudo bash -c` car `/root` n'est pas accessible a l'utilisateur elzouave.

### Voir les logs Traefik
```bash
sudo docker logs root-traefik-1 2>&1 | tail -20
```

### Voir les logs n8n
```bash
sudo docker logs root-n8n-1 2>&1 | tail -20
```

## 3. Mise a jour du code

```bash
cd /srv/online_form && git pull
sudo systemctl restart online-form
```

## 4. Gestion des admins

```bash
cd /srv/online_form && source venv/bin/activate

# Lister les admins
python3 backend/manage_admin.py list

# Creer un admin
python3 backend/manage_admin.py create <username>

# Changer un mot de passe
python3 backend/manage_admin.py passwd <username>

# Supprimer un admin (demande confirmation)
python3 backend/manage_admin.py delete <username>
```

## 5. Debugging

### Browser DevTools
Open with `Cmd+Option+I` (Mac) or `F12` (Windows/Linux). Useful for:
- **Console tab**: CSP violations, JavaScript errors, warnings
- **Network tab**: Failed API calls, 4xx/5xx responses, slow requests
- **Application tab**: localStorage content (tokens), cookies

### Server-side debugging
```bash
# Real-time application logs
sudo journalctl -u online-form -f

# Test manually with verbose curl
curl -kv https://form.srv1163941.hstgr.cloud 2>&1 | tail -20

# Test FastAPI directly (bypass Traefik)
curl http://127.0.0.1:8000

# Check Traefik logs
sudo docker logs root-traefik-1 2>&1 | tail -20
```

## 6. Troubleshooting

### 6.1 "Bad Gateway" sur form.srv1163941.hstgr.cloud

**Signification** : Traefik recoit la requete mais n'arrive pas a joindre FastAPI.

**Etapes de diagnostic :**

```bash
# 1. FastAPI tourne-t-il ?
sudo systemctl status online-form
curl http://127.0.0.1:8000

# 2. Traefik lit-il le fichier de routage ?
sudo docker exec root-traefik-1 ls /etc/traefik/dynamic/
# → doit afficher online-form.yml

# 3. Le contenu du fichier est-il correct ?
sudo docker exec root-traefik-1 cat /etc/traefik/dynamic/online-form.yml
# → verifier que url contient 172.17.0.1 (pas 127.17.0.1 ni 127.0.0.1)

# 4. Traefik peut-il atteindre FastAPI ?
sudo docker exec root-traefik-1 wget -qO- http://172.17.0.1:8000
# → doit retourner le HTML du formulaire

# 5. Curl verbeux pour plus de details
curl -kv https://form.srv1163941.hstgr.cloud 2>&1 | tail -20
```

**Causes courantes :**

| Symptome | Cause | Solution |
|----------|-------|----------|
| Bad Gateway | FastAPI ecoute sur `--host 127.0.0.1` | Changer en `--host 0.0.0.0` dans le service Systemd, puis `daemon-reload` + `restart` |
| Bad Gateway | Mauvaise IP dans online-form.yml | Corriger : `172.17.0.1` (IP du bridge Docker). Trouver l'IP : `ip addr show docker0 \| grep inet` |
| Bad Gateway | Section `servers` vide dans le YAML | Probleme d'indentation YAML — recreer le fichier avec `sudo tee` |
| 404 Not Found | Sous-domaine ne matche pas la rule | Verifier `Host(...)` dans `/root/traefik-config/online-form.yml` |

### 5.2 Le service FastAPI ne demarre pas

```bash
# Voir les erreurs
sudo journalctl -u online-form -n 30

# Verifier le fichier de service
cat /etc/systemd/system/online-form.service

# Tester manuellement
cd /srv/online_form/backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5.3 Impossible d'acceder a /root (Permission denied)

L'utilisateur `elzouave` n'a pas acces au dossier `/root`. Utiliser :
```bash
sudo bash -c "cd /root && <commande>"
```

## 7. Configuration du service Systemd

```ini
[Unit]
Description=Online Form - FastAPI (Universite de Ngaoundere)
After=network.target

[Service]
User=elzouave
Group=elzouave
WorkingDirectory=/srv/online_form/backend
ExecStart=/srv/online_form/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment="PATH=/srv/online_form/venv/bin"

[Install]
WantedBy=multi-user.target
```

### Explication des directives

| Directive | Role |
|-----------|------|
| `User=elzouave` | Le service tourne sous l'utilisateur elzouave (pas root) |
| `WorkingDirectory` | Repertoire de travail pour que les imports Python fonctionnent |
| `ExecStart` | Lance Uvicorn sur 0.0.0.0:8000 |
| `--host 0.0.0.0` | Ecoute sur toutes les interfaces (necessaire pour le bridge Docker 172.17.0.1) |
| `--port 8000` | Port interne de l'application |
| `Restart=always` | Redemarre automatiquement en cas de crash |
| `RestartSec=5` | Attend 5 secondes avant de redemarrer |
| `After=network.target` | Demarre apres que le reseau soit disponible |
| `WantedBy=multi-user.target` | Demarre au boot du serveur |

## 8. Gestion des assets (logo et favicon)

Les images sont stockees dans `frontend/assets/` :

| Fichier        | Dimensions | Usage                            |
|----------------|------------|----------------------------------|
| `logo.png`     | 400 × 400  | Logo affiche dans le header      |
| `favicon.png`  | 64 × 64    | Icone de l'onglet du navigateur  |

### Verifier les caracteristiques d'une image

```bash
# Dimensions et format
file frontend/assets/logo.png

# Taille fichier
ls -lh frontend/assets/

# Mode et transparence (necessite Pillow : pip install Pillow)
python3 -c "
from PIL import Image
img = Image.open('frontend/assets/logo.png')
print(f'Mode: {img.mode}, size: {img.size}')
print(f'Pixel coin (0,0): {img.getpixel((0, 0))}')
"
```

### Reduire la taille / dimensions d'une image

**Avec sips (preinstalle sur Mac, attention : ne preserve pas toujours la transparence)** :
```bash
# Redimensionner en gardant les proportions (max 400 px)
sips -Z 400 source.png --out output.png
```

**Avec Pillow (Python, preserve la transparence)** :
```bash
python3 -c "
from PIL import Image
img = Image.open('source.png')
img.thumbnail((400, 400), Image.LANCZOS)
img.save('output.png', 'PNG', optimize=True)
"
```

### Generer le logo et le favicon avec masque circulaire

Si le logo source a un fond gris/blanc opaque (cas frequent), il faut appliquer un masque
circulaire pour rendre les coins reellement transparents :

```bash
python3 << 'EOF'
from PIL import Image, ImageDraw

src = 'frontend/assets/source_logo.png'
img = Image.open(src).convert('RGBA')
size = img.size

# Masque circulaire avec antialiasing (dessine 4x plus grand puis reduit)
mask_size = (size[0] * 4, size[1] * 4)
mask = Image.new('L', mask_size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
mask = mask.resize(size, Image.LANCZOS)

# Appliquer le masque
result = Image.new('RGBA', size, (0, 0, 0, 0))
result.paste(img, (0, 0), mask)

# Generer logo.png (400x400)
logo = result.copy()
logo.thumbnail((400, 400), Image.LANCZOS)
logo.save('frontend/assets/logo.png', 'PNG', optimize=True)

# Generer favicon.png (64x64)
favicon = result.copy()
favicon.thumbnail((64, 64), Image.LANCZOS)
favicon.save('frontend/assets/favicon.png', 'PNG', optimize=True)

print('Logo et favicon generes avec succes')
EOF
```

### Verifier qu'une image est vraiment transparente

```bash
python3 -c "
from PIL import Image
img = Image.open('frontend/assets/logo.png')
if img.mode == 'RGBA':
    alphas = img.split()[3].histogram()
    transparent = alphas[0]
    opaque = alphas[255]
    total = sum(alphas)
    print(f'Transparents: {100*transparent/total:.1f}%')
    print(f'Opaques: {100*opaque/total:.1f}%')
"
```

> **Note** : Si tous les pixels sont opaques (100%), l'image n'est pas transparente, meme si
> l'apercu du systeme affiche un motif damier (qui peut etre genere par l'outil de prevue).

## 9. Pare-feu (ufw)

### Voir les regles actives
```bash
sudo ufw status verbose
```

### Ajouter une regle
```bash
sudo ufw allow <port>/tcp                        # Ouvrir un port
sudo ufw allow from <ip_range> to any port <port> # Restreindre a un reseau
```

### Supprimer une regle
```bash
sudo ufw status numbered   # Voir les numeros
sudo ufw delete <numero>   # Supprimer par numero
```

### Desactiver / Reactiver
```bash
sudo ufw disable   # Desactiver
sudo ufw enable    # Reactiver
```

### Troubleshooting — Gateway Timeout apres activation de ufw

Docker utilise des reseaux internes (bridges) pour communiquer. Si le pare-feu bloque
ces reseaux, Traefik ne peut plus atteindre FastAPI.

```bash
# Trouver l'IP source utilisee par Traefik
sudo journalctl -u online-form -n 20
# → Chercher l'IP dans les logs (ex: 172.18.0.3)

# Autoriser le reseau correspondant
sudo ufw allow from 172.18.0.0/16 to any port 8000

# Si le trafic route est bloque
sudo ufw default allow routed
```

## 10. Configuration du routage Traefik

Fichier : `/root/traefik-config/online-form.yml`

```yaml
http:
  routers:
    online-form:
      rule: "Host(`form.srv1163941.hstgr.cloud`)"
      entryPoints:
        - web
        - websecure
      service: online-form
      tls:
        certResolver: mytlschallenge
  services:
    online-form:
      loadBalancer:
        servers:
          - url: "http://172.17.0.1:8000"
```

> **172.17.0.1** est l'IP du host vu depuis les conteneurs Docker (bridge `docker0`).
> Pour la retrouver : `ip addr show docker0 | grep inet`

## 11. Database Backup

Script: `/srv/online_form/scripts/backup.sh`
Backups stored in: `/srv/online_form/backups/`
Retention: last 30 backups.

### Run a manual backup
```bash
/srv/online_form/scripts/backup.sh
```

### List existing backups
```bash
ls -lh /srv/online_form/backups/
```

### Restore from a backup
```bash
# Stop the service
sudo systemctl stop online-form

# Replace the database with a backup
cp /srv/online_form/backups/responses_YYYYMMDD_HHMMSS.db /srv/online_form/backend/responses.db

# Restart the service
sudo systemctl start online-form
```

### Cron job (daily at 3 AM)
```bash
# Edit crontab
crontab -e

# Add this line:
0 3 * * * /srv/online_form/scripts/backup.sh
```

### Verify cron is active
```bash
crontab -l
```

## 12. Fail2ban

Config: `/etc/fail2ban/jail.local`
Filter: `/etc/fail2ban/filter.d/online-form-login.conf`

### Check status
```bash
sudo fail2ban-client status
sudo fail2ban-client status online-form-login
sudo fail2ban-client status sshd
```

### Unban an IP
```bash
sudo fail2ban-client set online-form-login unbanip <IP>
sudo fail2ban-client set sshd unbanip <IP>
```

### View banned IPs
```bash
sudo fail2ban-client status online-form-login | grep "Banned IP"
```

### Restart after config change
```bash
sudo systemctl restart fail2ban
```
