# Guide de deploiement — VPS Hostinger

> Derniere mise a jour : 2026-04-07
> Serveur : 72.62.50.19 (srv1163941.hstgr.cloud)

## Vue d'ensemble

```
Repondant (navigateur)
      |
  Internet
      |
  VPS (72.62.50.19)
      |
  Traefik (ports 80/443) -- Reverse proxy + SSL
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
| 4   | Configurer l'application   | En cours     |
| 5   | Configurer Systemd         | A faire      |
| 6   | Configurer Traefik         | A faire      |
| 7   | Configurer le pare-feu     | A faire      |
| 8   | SSL (HTTPS)                | A faire      |

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

**Pourquoi** : Creer l'environnement Python, installer les dependances, configurer les variables d'environnement.

```bash
# Creer le venv et installer les dependances
cd /srv/online_form
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Creer le fichier .env
# (commandes a completer)

# Creer le compte admin
# (commandes a completer)
```

> **Statut : En cours**

---

## Etape 5 — Configurer Systemd

**Pourquoi** : Pour que l'application demarre automatiquement et redemarre en cas de crash.

> **Statut : A faire**

---

## Etape 6 — Configurer Traefik

**Pourquoi** : Pour exposer l'application sur internet via HTTPS.

> **Statut : A faire**
> Note : On utilise Traefik (deja en place) au lieu de Nginx.

---

## Etape 7 — Configurer le pare-feu

**Pourquoi** : Ouvrir uniquement les ports necessaires (22, 80, 443).

> **Statut : A faire**

---

## Etape 8 — SSL (HTTPS)

**Pourquoi** : Securiser la connexion avec un certificat Let's Encrypt.

> **Statut : A faire**
> Note : Traefik gere deja le SSL automatiquement — cette etape sera probablement integree a l'etape 6.
