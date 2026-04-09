# Liste des taches a faire

> Liste persistante des taches futures du projet, ordonnees par priorite.
> Derniere mise a jour : 2026-04-09

## Ordre de priorite recommande

| Ordre | Priorite | Tache | Raison |
|-------|----------|-------|--------|
| 1 | Haute | Journal des connexions admin (table dediee + dashboard) | Securite, vue centralisee dans le dashboard |
| 2 | Moyenne | Cache busting des fichiers statiques | Ameliore l'experience utilisateur apres chaque mise a jour |
| 3 | Basse | Console d'administration web | Confort, le CLI manage_admin.py fonctionne deja |

---

## 1. Journal des connexions admin (vue dashboard)

**Priorite** : Haute
**Statut** : A faire

### Contexte
Les tentatives de connexion sont deja loggees via le systeme de logs (visible avec
`sudo journalctl -u online-form | grep "Admin login"`). Cette tache vise a aller plus loin
en stockant l'historique en base et en l'affichant dans le dashboard admin.

### Donnees a enregistrer
- Username tente
- Date/heure (UTC)
- IP source
- Succes ou echec
- User-Agent (optionnel)

### Implementation
- Creer une table `login_history` (id, username, timestamp, ip, success, user_agent)
- Ajouter l'enregistrement dans la fonction `login` de `main.py`
- Nouvelle section dans le dashboard avec les 50 dernieres tentatives
- Filtres : par username, par succes/echec, par periode

---

## 2. Cache busting des fichiers statiques

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

## 3. Console d'administration web

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
- Log de chaque operation (deja en place via le systeme de logs)

### Note
Le script `backend/manage_admin.py` fonctionne deja et est suffisant pour un usage basique.
Cette tache est une amelioration de confort, pas une necessite.

---

## Taches terminees

- **Systeme de logs a l'application** (commit `30d90d2`) — module `logging_config.py`,
  logs sur soumissions, login, exports et operations admin. Sortie vers stdout, capture
  par journald (`sudo journalctl -u online-form -f`).
