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

## 5. Troubleshooting

### 5.1 "Bad Gateway" sur form.srv1163941.hstgr.cloud

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

## 6. Configuration du service Systemd

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

## 7. Pare-feu (ufw)

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

## 8. Configuration du routage Traefik

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
