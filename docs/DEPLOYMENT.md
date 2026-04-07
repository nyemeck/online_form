# Guide de deploiement — VPS Hostinger

> Derniere mise a jour : 2026-04-08
> Serveur : 72.62.50.19 (srv1163941.hstgr.cloud)

## Vue d'ensemble

```
Repondant (navigateur)
      |
  Internet
      |
  VPS (72.62.50.19)
      |
  Traefik (ports 80/443) -- Reverse proxy + SSL automatique
      |
  Uvicorn/FastAPI (port 8000) -- Application
      |
  SQLite (responses.db) -- Base de donnees
```

## Etapes du deploiement

| #   | Etape                      | Statut       |
|-----|----------------------------|--------------|
| 1   | Verifier l'etat du serveur | Fait         |
| 2   | Installer les prerequis    | Fait         |
| 3   | Transferer le code         | Fait         |
| 4   | Configurer l'application   | Fait         |
| 5   | Configurer Systemd         | Fait         |
| 6   | Configurer Traefik         | Fait         |
| 7   | Configurer le pare-feu     | Fait         |
| 8   | SSL (HTTPS)                | Fait (via Traefik) |

---

## Etape 1 — Verifier l'etat du serveur

**Pourquoi** : Savoir ce qui est deja installe avant de commencer.

```bash
# Systeme
cat /etc/os-release | head -4
# → Ubuntu 24.04.3 LTS (Noble Numbat)

# Python
python3 --version
# → Python 3.12.3

# Docker
docker --version && docker compose version
# → Docker 29.2.1, Docker Compose 5.0.2

# Git
git --version
# → git 2.43.0

# Ressources
df -h / && echo "---" && free -h && echo "---" && nproc
# → 48 Go disque, 3.8 Go RAM, 1 vCPU

# Services Docker actifs
docker ps
# → Traefik (ports 80/443) + n8n (port 5678)
```

**Resultat** : Traefik occupe deja les ports 80/443 → on utilisera Traefik au lieu de Nginx.

---

## Etape 2 — Installer les prerequis

**Pourquoi** : Installer les outils necessaires pour faire tourner l'application.

```bash
# pip et venv n'etaient pas installes
sudo apt update && sudo apt install -y python3-pip python3-venv

# Nginx (installe mais inutilise — Traefik est deja en place)
sudo apt install -y nginx
# Note : Nginx ne demarre pas car Traefik occupe le port 80
```

---

## Etape 3 — Transferer le code

**Pourquoi** : Mettre le code source sur le serveur.

### 3.1 Configuration GitHub (Mac local)

```bash
# Generer une cle SSH pour le compte GitHub prive
ssh-keygen -t ed25519 -C "nyemeckpaulalex@gmail.com" -f ~/.ssh/id_private_github_nyemeck

# Sauvegarder la passphrase dans le Keychain macOS
ssh-add --apple-use-keychain ~/.ssh/id_private_github_nyemeck

# Copier la cle publique pour l'ajouter sur GitHub (Settings → SSH keys)
pbcopy < ~/.ssh/id_private_github_nyemeck.pub
```

Configuration SSH (`~/.ssh/config` sur Mac) :
```
Host private_github
    HostName github.com
    User git
    UseKeychain yes
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_private_github_nyemeck
```

```bash
# Configurer le remote et push
git remote set-url origin git@private_github:nyemeck/online_form.git
git push -u origin master
```

### 3.2 Deploy key sur le VPS (lecture seule)

```bash
# Sur le VPS : generer une cle dediee au depot
ssh-keygen -t ed25519 -C "deploy-online-form" -f ~/.ssh/id_deploy_online_form
cat ~/.ssh/id_deploy_online_form.pub
# → Ajouter sur GitHub : Depot → Settings → Deploy keys (sans write access)
```

Configuration SSH (`~/.ssh/config` sur VPS) :
```
Host github-deploy
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_deploy_online_form
```

```bash
# Tester la connexion
ssh -T github-deploy
# → Hi nyemeck/online_form! You've successfully authenticated...

# Cloner le depot
git clone git@github-deploy:nyemeck/online_form.git

# Deplacer vers l'emplacement definitif
sudo mv ~/online_form /srv/online_form
sudo chown -R elzouave:elzouave /srv/online_form
```

---

## Etape 4 — Configurer l'application

**Pourquoi** : Creer l'environnement Python, installer les dependances, configurer les variables et le compte admin.

```bash
# Creer le venv et installer les dependances
cd /srv/online_form
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Generer la SECRET_KEY et creer le .env
cd /srv/online_form/backend
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env

# Creer le premier compte admin
cd /srv/online_form
python3 backend/manage_admin.py create admin
# Le mot de passe est demande de maniere masquee (min. 8 caracteres)
```

---

## Etape 5 — Configurer Systemd

**Pourquoi** : Pour que l'application demarre automatiquement et redemarre en cas de crash.

### 5.1 Creer le fichier de service

```bash
sudo nano /etc/systemd/system/online-form.service
```

Contenu :
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

> **Note** : `--host 0.0.0.0` est necessaire car Traefik (dans Docker) accede a FastAPI
> via l'interface bridge Docker (172.17.0.1). Avec `127.0.0.1`, Traefik ne peut pas
> joindre l'application et retourne "Bad Gateway".

### 5.2 Activer et demarrer le service

```bash
sudo systemctl daemon-reload    # Relit les fichiers de service
sudo systemctl enable online-form  # Demarrage automatique au boot
sudo systemctl start online-form   # Demarrer maintenant
```

### 5.3 Verifier

```bash
sudo systemctl status online-form
# → active (running)

curl http://127.0.0.1:8000
# → HTML du formulaire
```

---

## Etape 6 — Configurer Traefik

**Pourquoi** : Pour exposer l'application sur internet via HTTPS. Traefik est deja en place
(il gere n8n), on ajoute un routage pour FastAPI.

**Probleme** : Traefik tourne dans Docker, FastAPI tourne sur le host (Systemd).
Traefik ne peut pas acceder directement a `127.0.0.1:8000` du host depuis son conteneur.

**Solution** : Utiliser l'IP du bridge Docker (`172.17.0.1`) pour que Traefik atteigne le host,
et un fichier de configuration (file provider) pour definir le routage.

### 6.1 Creer le fichier de routage

```bash
sudo mkdir -p /root/traefik-config
sudo nano /root/traefik-config/online-form.yml
```

Contenu :
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

> **Important** : L'URL est `172.17.0.1` (IP du host vu depuis Docker), pas `127.0.0.1`.
> Pour trouver cette IP : `ip addr show docker0 | grep inet`

### 6.2 Modifier le docker-compose.yml

```bash
sudo nano /root/docker-compose.yml
```

Ajouter 4 elements au bloc `traefik` :

**a)** Dans `command:`, apres `--providers.docker.exposedbydefault=false` :
```yaml
      - "--providers.file.directory=/etc/traefik/dynamic"
      - "--providers.file.watch=true"
```

**b)** Apres le bloc `ports:` :
```yaml
    extra_hosts:
      - "host-gateway:host-gateway"
```

**c)** Dans `volumes:`, ajouter :
```yaml
      - /root/traefik-config:/etc/traefik/dynamic:ro
```

### 6.3 Redemarrer Traefik

```bash
sudo bash -c "cd /root && docker compose down && docker compose up -d"
```

> **Note** : On utilise `sudo bash -c` car `/root` n'est pas accessible a l'utilisateur elzouave.

### 6.4 Verifier

```bash
# Verifier que les conteneurs tournent
sudo docker ps
# → root-traefik-1 et root-n8n-1 en "Up"

# Tester l'acces depuis le VPS
curl -k https://form.srv1163941.hstgr.cloud
# → HTML du formulaire

# Tester dans le navigateur
# → https://form.srv1163941.hstgr.cloud
```

### 6.5 Troubleshooting — "Bad Gateway"

Si `curl` retourne `Bad Gateway`, voici les etapes de diagnostic :

```bash
# 1. Verifier que FastAPI tourne
sudo systemctl status online-form
curl http://127.0.0.1:8000

# 2. Verifier que Traefik lit le fichier de config
sudo docker exec root-traefik-1 ls /etc/traefik/dynamic/
# → doit afficher online-form.yml

# 3. Verifier le contenu du fichier dans le conteneur
sudo docker exec root-traefik-1 cat /etc/traefik/dynamic/online-form.yml
# → verifier que l'URL du serveur est presente et correcte (172.17.0.1, pas 127.17.0.1)

# 4. Tester la connectivite depuis Traefik vers FastAPI
sudo docker exec root-traefik-1 wget -qO- http://172.17.0.1:8000
# → doit retourner le HTML du formulaire

# 5. Verifier les logs Traefik
sudo docker logs root-traefik-1 2>&1 | tail -20

# 6. Curl verbeux pour plus de details
curl -kv https://form.srv1163941.hstgr.cloud 2>&1 | tail -20
```

**Erreurs courantes :**

| Symptome | Cause | Solution |
|----------|-------|----------|
| Bad Gateway | FastAPI ecoute sur 127.0.0.1 | Changer `--host` en `0.0.0.0` dans le service Systemd |
| Bad Gateway | Mauvaise IP dans online-form.yml | Verifier : `172.17.0.1` (pas `127.17.0.1`) |
| Bad Gateway | Section `servers` vide dans le YAML | Probleme d'indentation — recreer le fichier |
| 404 Not Found | Le sous-domaine ne matche pas | Verifier la `rule` dans online-form.yml |

---

## Etape 7 — Configurer le pare-feu (ufw)

**Pourquoi** : Sans pare-feu, tous les ports sont accessibles depuis internet. Par exemple,
quelqu'un pourrait acceder directement a `http://72.62.50.19:8000` et contourner Traefik (pas de SSL).
Le pare-feu limite l'acces aux seuls ports necessaires.

### 7.1 Ouvrir les ports necessaires et activer

```bash
# Autoriser SSH (CRITIQUE — sinon on perd l'acces au serveur)
sudo ufw allow 22/tcp

# Autoriser HTTP et HTTPS (pour Traefik)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le pare-feu (taper 'y' pour confirmer)
sudo ufw enable
```

### 7.2 Autoriser Docker a atteindre FastAPI

Apres activation de ufw, Traefik (dans Docker) ne peut plus joindre FastAPI sur le port 8000
car le trafic est bloque. Docker utilise des reseaux internes (bridges) dont les IPs
peuvent varier.

```bash
# Autoriser le reseau Docker bridge par defaut (docker0)
sudo ufw allow from 172.17.0.0/16 to any port 8000

# Autoriser le reseau Docker Compose (utilise par Traefik)
# Traefik accede depuis 172.18.0.x, pas 172.17.0.x
sudo ufw allow from 172.18.0.0/16 to any port 8000

# Autoriser le trafic route (necessaire pour Docker)
sudo ufw default allow routed
```

> **Comment on a trouve ces IPs** : Les logs Uvicorn montrent l'IP source des requetes
> de Traefik (`172.18.0.3`). On peut aussi verifier avec :
> `ip addr show docker0 | grep inet` → `172.17.0.1`
> `docker network inspect root_default | grep Subnet` → `172.18.0.0/16`

### 7.3 Verifier

```bash
sudo ufw status verbose
```

Resultat attendu :
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), allow (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
8000                       ALLOW IN    172.17.0.0/16
8000                       ALLOW IN    172.18.0.0/16
22/tcp (v6)                ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

Tester que tout fonctionne :
```bash
# Via Traefik (doit fonctionner)
curl -k https://form.srv1163941.hstgr.cloud

# Depuis le Mac — acces direct au port 8000 (doit echouer/timeout)
# curl -m 5 http://72.62.50.19:8000
```

### 7.4 Troubleshooting — "Gateway Timeout" apres activation de ufw

**Signification** : Traefik recoit la requete mais le pare-feu bloque la connexion vers FastAPI.

**Etapes de diagnostic :**

```bash
# 1. Verifier les regles ufw
sudo ufw status verbose
# → Verifier que les reseaux Docker sont autorises sur le port 8000

# 2. Verifier depuis quel IP Traefik accede a FastAPI
sudo journalctl -u online-form -n 20
# → Les logs Uvicorn montrent l'IP source (ex: 172.18.0.3)

# 3. Tester la connectivite depuis Traefik
sudo docker exec root-traefik-1 wget -qO- http://172.17.0.1:8000
# → Si ca tourne indefiniment, le pare-feu bloque

# 4. Verifier la politique de routage
sudo ufw status verbose | grep routed
# → Doit etre "allow (routed)", pas "deny (routed)"
```

**Causes courantes :**

| Symptome | Cause | Solution |
|----------|-------|----------|
| Gateway Timeout | Reseau Docker non autorise | `sudo ufw allow from 172.18.0.0/16 to any port 8000` |
| Gateway Timeout | Trafic route bloque | `sudo ufw default allow routed` |
| Gateway Timeout | Docker utilise un autre reseau | Verifier les logs Uvicorn pour l'IP source, puis autoriser le bon sous-reseau |

---

## Etape 8 — SSL (HTTPS)

**Statut : Fait** — Traefik gere automatiquement les certificats Let's Encrypt via le `certResolver: mytlschallenge`.
Le certificat est genere automatiquement lors du premier acces a `https://form.srv1163941.hstgr.cloud`.
