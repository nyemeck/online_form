# Documentation Serveur VPS — Hostinger

> Derniere mise a jour : 2026-04-07

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
| **Pare-feu (ufw)** | Inactif     |

## 3. Logiciels installes

| Logiciel       | Version   | Notes                                           |
|----------------|-----------|-------------------------------------------------|
| Python         | 3.12.3    | Installe par defaut avec Ubuntu 24.04           |
| pip            | —         | Installe manuellement (python3-pip)             |
| venv           | —         | Installe manuellement (python3-venv)            |
| Git            | 2.43.0    | Installe par defaut                             |
| Docker         | 29.2.1    | Moteur de conteneurs                            |
| Docker Compose | 5.0.2     | Plugin Docker (v2)                              |
| Nginx          | —         | Installe mais **inactif** (conflit port 80 avec Traefik) |

## 4. Services actifs (Docker)

Tous les services tournent via Docker Compose depuis `/root/docker-compose.yml`.
Variables d'environnement dans `/root/.env`.

### 4.1 Traefik (reverse proxy)

| Element              | Valeur                                    |
|----------------------|-------------------------------------------|
| **Image**            | traefik (latest)                          |
| **Conteneur**        | root-traefik-1                            |
| **Ports exposes**    | 0.0.0.0:80 → 80, 0.0.0.0:443 → 443      |
| **Role**             | Reverse proxy + terminaison SSL           |
| **SSL**              | Let's Encrypt (TLS challenge, automatique)|
| **Email ACME**       | user@srv1163941.hstgr.cloud               |
| **Stockage certs**   | Volume `traefik_data` → /letsencrypt      |
| **Provider**         | Docker (decouverte auto via labels)       |
| **Redirection HTTP** | Oui (80 → 443 automatique)               |

### 4.2 n8n (automatisation workflows)

| Element           | Valeur                                     |
|-------------------|--------------------------------------------|
| **Image**         | docker.n8n.io/n8nio/n8n (v1.121.3)        |
| **Conteneur**     | root-n8n-1                                 |
| **Port interne**  | 127.0.0.1:5678 → 5678                     |
| **URL publique**  | https://n8n.srv1163941.hstgr.cloud         |
| **Donnees**       | Volume `n8n_data` → /home/node/.n8n        |
| **Fichiers**      | /local-files → /files                      |
| **Timezone**      | Europe/Berlin                              |

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
  |-- Host: n8n.srv1163941.hstgr.cloud --> n8n (port 5678)
  |-- Host: [a configurer]             --> FastAPI (port 8000)
      |
      v
Nginx (installe, inactif — non utilise)
```

## 6. Ports utilises

| Port | Protocole | Utilise par       | Acces          |
|------|-----------|-------------------|----------------|
| 22   | TCP       | SSH               | Externe        |
| 80   | TCP       | Traefik (Docker)  | Externe        |
| 443  | TCP       | Traefik (Docker)  | Externe        |
| 5678 | TCP       | n8n (Docker)      | 127.0.0.1 only |
| 8000 | TCP       | FastAPI (a venir) | A configurer   |

## 7. Applications deployees

| Application  | Emplacement              | Depot GitHub                         | Methode de deploy |
|--------------|--------------------------|--------------------------------------|--------------------|
| online_form  | `/srv/online_form`       | nyemeck/online_form (prive)          | Deploy key SSH (lecture seule) |

## 8. Cles SSH

| Cle                                        | Usage                              |
|--------------------------------------------|------------------------------------|
| `~/.ssh/id_deploy_online_form`             | Deploy key pour le depot online_form |
| Config SSH : `Host github-deploy`          | Alias pour clone/pull via deploy key |

## 9. Fichiers de configuration cles

| Fichier                    | Contenu                                      |
|----------------------------|----------------------------------------------|
| `/root/docker-compose.yml` | Definition des services Traefik + n8n         |
| `/root/.env`               | Variables : DOMAIN_NAME, SUBDOMAIN, SSL_EMAIL |
| `~/.ssh/config`            | Alias SSH pour deploy key GitHub              |

## 10. Volumes Docker

| Volume        | Utilise par | Contenu                    |
|---------------|-------------|----------------------------|
| traefik_data  | Traefik     | Certificats SSL (acme.json)|
| n8n_data      | n8n         | Donnees et config n8n      |

## 11. Points d'attention

- **Pas de swap** : En cas de pic memoire, le systeme peut tuer des processus (OOM killer)
- **Pare-feu inactif** : Tous les ports sont ouverts — a securiser avant mise en production
- **Nginx installe mais inutilise** : Traefik remplit deja le role de reverse proxy
- **1 seul vCPU** : Limiter le nombre de workers Uvicorn en consequence
- **Traefik gere le SSL** : Pas besoin de Certbot separement
