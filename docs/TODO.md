# Liste des taches a faire

> Liste persistante des taches futures du projet, ordonnees par priorite.
> Derniere mise a jour : 2026-04-09

## Ordre de priorite recommande

| Ordre | Priorite | Tache | Raison |
|-------|----------|-------|--------|
| 1 | Haute | Systeme de logs a l'application | Fondation, indispensable en production pour debugging et audit |
| 2 | Haute | Journal des connexions admin | Securite. Devient simple une fois le systeme de logs en place |
| 3 | Moyenne | Cache busting des fichiers statiques | Ameliore l'experience utilisateur apres chaque mise a jour |
| 4 | Basse | Console d'administration web | Confort, le CLI manage_admin.py fonctionne deja |

---

## 1. Systeme de logs a l'application

**Priorite** : Haute
**Statut** : A faire

### Description
Mettre en place un systeme de logging Python (module `logging`) pour tracer les actions importantes :
- Soumissions de formulaires (avec ID, langue, statut)
- Erreurs et exceptions (stack trace)
- Connexions admin (succes/echec)
- Operations sur les comptes admins (create, passwd, delete)
- Exports CSV/Excel

### Considerations techniques
- Utiliser le module `logging` standard de Python
- Niveaux : DEBUG, INFO, WARNING, ERROR, CRITICAL
- Format : timestamp, niveau, module, message
- Sortie : stdout (capture par journald via Systemd)
- Permettre d'augmenter la verbosite via une variable d'environnement (`LOG_LEVEL`)
- Eviter de logger des donnees sensibles (mots de passe, tokens)

### Comment consulter les logs apres implementation
```bash
sudo journalctl -u online-form -f               # Temps reel
sudo journalctl -u online-form -n 100           # 100 dernieres lignes
sudo journalctl -u online-form --since "1 hour ago"
```

---

## 2. Journal des connexions admin

**Priorite** : Haute
**Statut** : A faire (depend de la tache 1)

### Description
Enregistrer chaque tentative de connexion admin pour detecter des activites suspectes
et tracer l'activite des administrateurs.

### Donnees a enregistrer
- Username tente
- Date/heure (UTC)
- IP source
- Succes ou echec
- User-Agent (optionnel)

### Implementation
- **Option A** : Via le systeme de logs (tache 1) — simple, visible dans journalctl
- **Option B** : Table `login_history` en base — permet d'afficher dans le dashboard

### Affichage
- Si Option A : visible via `sudo journalctl -u online-form | grep "login"`
- Si Option B : nouvelle section dans le dashboard admin avec les 50 dernieres tentatives

---

## 3. Cache busting des fichiers statiques

**Priorite** : Moyenne
**Statut** : A faire

### Description
Eviter que les utilisateurs aient des versions obsoletes des fichiers JSON, JS et CSS
apres un deploiement (probleme rencontre lors du deploiement de la modification GECAM).

### Approche recommandee : version manuelle
Definir une constante `APP_VERSION` dans les JS et l'ajouter aux URLs des fichiers statiques.

### Implementation
**Dans `frontend/js/app.js`, `frontend/js/dashboard.js` et le script inline de `login.html`** :
```js
const APP_VERSION = "1.0.1";

fetch(`/static/lang/${lang}.json?v=${APP_VERSION}`)
```

**Dans les HTML** :
```html
<link rel="stylesheet" href="/static/css/style.css?v=1.0.1">
<script src="/static/js/app.js?v=1.0.1"></script>
```

### Workflow
- Incrementer `APP_VERSION` a chaque modification de fichier statique
- Mettre a jour la version dans tous les fichiers concernes (HTML + JS)

### Alternative future
Generer automatiquement la version depuis le hash du commit git ou un timestamp de build.

---

## 4. Console d'administration web

**Priorite** : Basse
**Statut** : A faire

### Description
Interface web pour gerer les admins (creer, modifier mot de passe, supprimer)
sans passer par la ligne de commande.

### Pages a creer
- Liste des admins
- Formulaire de creation
- Formulaire de changement de mot de passe
- Confirmation de suppression

### Securite
- Accessible uniquement aux admins authentifies
- Confirmation pour les operations destructives
- Log de chaque operation (depend de la tache 1)

### Note
Le script `backend/manage_admin.py` fonctionne deja et est suffisant pour un usage basique.
Cette tache est une amelioration de confort, pas une necessite.
