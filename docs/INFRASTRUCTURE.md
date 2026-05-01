# Infrastructure — VPS Hostinger

> Derniere mise a jour : 2026-04-08

## 1. Informations systeme

| Element       | Valeur                              |
|---------------|-------------------------------------|
| **OS**        | Ubuntu 24.04.3 LTS (Noble Numbat)  |
| **IP**        | 72.62.50.19                         |
| **Domaine**   | srv1163941.hstgr.cloud              |
| **CPU**       | 1 vCPU — AMD EPYC 9354P 32-Core    |
| **RAM**       | 3.8 Go (pas de swap configure)      |
| **Disque**    | 48 Go (/dev/sda1) — 15% utilise    |
| **Hebergeur** | Hostinger VPS                       |

## 2. Acces

| Element            | Valeur       |
|--------------------|--------------|
| **Utilisateur SSH**| elzouave     |
| **Droits sudo**    | Oui          |
| **Pare-feu (ufw)** | Actif (22, 80, 443 ouverts + Docker autorise) |

## 3. Logiciels installes

| Logiciel       | Version   | Notes                                           |
|----------------|-----------|-------------------------------------------------|
| Python         | 3.12.3    | Installe par defaut avec Ubuntu 24.04           |
| pip            | —         | Installe manuellement (python3-pip)             |
| venv           | —         | Installe manuellement (python3-venv)            |
| Git            | 2.43.0    | Installe par defaut                             |
| Docker         | 29.2.1    | Moteur de conteneurs                            |
| Docker Compose | 5.0.2     | Plugin Docker (v2)                              |
| ~~Nginx~~      | —         | Desinstalle (conflit port 80 avec Traefik au boot) |

## 4. Services actifs

### 4.1 Services Docker (via `/root/docker-compose.yml`)

Variables d'environnement dans `/root/.env`.

#### Traefik (reverse proxy)

| Element              | Valeur                                    |
|----------------------|-------------------------------------------|
| **Image**            | traefik (latest)                          |
| **Conteneur**        | root-traefik-1                            |
| **Ports exposes**    | 0.0.0.0:80 → 80, 0.0.0.0:443 → 443      |
| **Role**             | Reverse proxy + terminaison SSL           |
| **SSL**              | Let's Encrypt (TLS challenge, automatique)|
| **Email ACME**       | user@srv1163941.hstgr.cloud               |
| **Stockage certs**   | Volume `traefik_data` → /letsencrypt      |
| **Providers**        | Docker (labels) + File (`/root/traefik-config/`) |
| **Redirection HTTP** | Oui (80 → 443 automatique)               |
| **Config dynamique** | `/root/traefik-config/` monte en lecture seule |

#### n8n (automatisation workflows)

| Element           | Valeur                                     |
|-------------------|--------------------------------------------|
| **Image**         | docker.n8n.io/n8nio/n8n (v1.121.3)        |
| **Conteneur**     | root-n8n-1                                 |
| **Port interne**  | 127.0.0.1:5678 → 5678                     |
| **URL publique**  | https://n8n.srv1163941.hstgr.cloud         |
| **Donnees**       | Volume `n8n_data` → /home/node/.n8n        |
| **Fichiers**      | /local-files → /files                      |
| **Timezone**      | Europe/Berlin                              |

### 4.2 Services Systemd

#### online-form (FastAPI)

| Element           | Valeur                                           |
|-------------------|--------------------------------------------------|
| **Fichier**       | `/etc/systemd/system/online-form.service`        |
| **Utilisateur**   | elzouave                                         |
| **Repertoire**    | `/srv/online_form/backend`                       |
| **Commande**      | uvicorn main:app --host 0.0.0.0 --port 8000     |
| **Port**          | 8000 (toutes interfaces)                         |
| **URL publique**  | https://form.srv1163941.hstgr.cloud              |
| **Redemarrage**   | Automatique (5s apres crash)                     |
| **Boot**          | Actif (enabled)                                  |

## 5. Architecture reseau

```
Navigateur (internet)
      |
      v
VPS 72.62.50.19
      |
      v
Traefik (Docker, ports 80/443)
  |-- HTTPS redirect automatique
  |-- SSL Let's Encrypt
  |
  |-- Host: n8n.srv1163941.hstgr.cloud  --> n8n (Docker, port 5678)
  |-- Host: form.srv1163941.hstgr.cloud --> FastAPI (Systemd, port 8000 via 172.17.0.1)
```

> **Note** : Traefik (dans Docker) atteint FastAPI (sur le host) via l'IP du bridge Docker
> `172.17.0.1`. C'est configure dans `/root/traefik-config/online-form.yml`.

## 6. Ports utilises

| Port | Protocole | Utilise par       | Acces              |
|------|-----------|-------------------|--------------------|
| 22   | TCP       | SSH               | Externe            |
| 80   | TCP       | Traefik (Docker)  | Externe            |
| 443  | TCP       | Traefik (Docker)  | Externe            |
| 5678 | TCP       | n8n (Docker)      | 127.0.0.1 only     |
| 8000 | TCP       | FastAPI (Systemd) | Docker uniquement (172.17.0.0/16, 172.18.0.0/16) |

## 7. Applications deployees

| Application  | Emplacement        | Depot GitHub                | Methode de deploy              | URL publique                          |
|--------------|--------------------|------------------------------|--------------------------------|---------------------------------------|
| online_form  | `/srv/online_form` | nyemeck/online_form (prive) | Deploy key SSH (lecture seule) | https://form.srv1163941.hstgr.cloud   |

## 8. Cles SSH

| Cle                                        | Usage                              |
|--------------------------------------------|------------------------------------|
| `~/.ssh/id_deploy_online_form`             | Deploy key pour le depot online_form |
| Config SSH : `Host github-deploy`          | Alias pour clone/pull via deploy key |

## 9. Fichiers de configuration cles

| Fichier                              | Contenu                                       |
|--------------------------------------|-----------------------------------------------|
| `/root/docker-compose.yml`           | Definition des services Traefik + n8n          |
| `/root/.env`                         | Variables : DOMAIN_NAME, SUBDOMAIN, SSL_EMAIL  |
| `/root/traefik-config/online-form.yml` | Routage Traefik → FastAPI (172.17.0.1:8000)  |
| `/etc/systemd/system/online-form.service` | Service Systemd pour FastAPI              |
| `/srv/online_form/backend/.env`      | SECRET_KEY pour JWT                            |
| `~/.ssh/config`                      | Alias SSH pour deploy key GitHub               |

## 10. Volumes Docker

| Volume        | Utilise par | Contenu                    |
|---------------|-------------|----------------------------|
| traefik_data  | Traefik     | Certificats SSL (acme.json)|
| n8n_data      | n8n         | Donnees et config n8n      |

## 11. Points d'attention

- **Pas de swap** : En cas de pic memoire, le systeme peut tuer des processus (OOM killer)
- **Pare-feu actif** : Seuls les ports 22, 80, 443 sont ouverts. Port 8000 restreint aux reseaux Docker
- **Nginx desinstalle** : Was causing port 80 conflict with Traefik on server reboot
- **1 seul vCPU** : Limiter le nombre de workers Uvicorn en consequence
- **Traefik gere le SSL** : Pas besoin de Certbot separement
- **FastAPI ecoute sur 0.0.0.0** : Necessaire pour le bridge Docker. Le pare-feu bloque l'acces direct au port 8000 depuis l'exterieur
