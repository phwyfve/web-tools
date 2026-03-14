# LMNP Manager - Guide d'utilisation

## 🚀 Démarrage rapide

### Installation
```bash
cd webapp-lmnp
npm install
```

### Lancement en développement
```bash
npm run dev
```

L'application sera accessible sur http://localhost:5173

### Connexion
Pour vous connecter, utilisez n'importe quelle adresse email et un mot de passe (l'authentification est simulée pour le moment).

## 📱 Fonctionnalités

### 1. Tableau de bord (Page 0)
- Vue d'ensemble des statistiques : revenus, dépenses, logements, documents
- Activité récente
- Liste des tâches à faire

### 2. SIREN (Page 2)
- Enregistrement des informations d'entreprise
- Numéro SIREN, raison sociale, forme juridique
- Adresse complète

### 3. Logements (Page 3)
- Ajout et gestion de vos biens immobiliers
- Informations détaillées : type, surface, adresse, date d'acquisition
- Vue en cartes avec possibilité de suppression

### 4. Usage du logement (Page 4)
- Configuration de l'utilisation de chaque logement
- Type d'usage (location meublée, saisonnière, courte durée)
- Taux d'occupation et loyer mensuel

### 5. Recettes (Page 5)
- Suivi de tous les revenus locatifs
- Ajout de loyers, charges, cautions
- Total des recettes affiché en temps réel
- Tableau détaillé avec possibilité de suppression

### 6. Dépenses (Page 6)
- Gestion des charges et dépenses
- Catégories : réparation, entretien, taxes, assurance, travaux
- Total des dépenses calculé automatiquement
- Historique complet en tableau

### 7. Emprunts (Page 7)
- Suivi de vos prêts immobiliers
- Informations : banque, montant, taux, durée, mensualité
- Vue détaillée par emprunt
- Calcul automatique des échéances

### 8. OGA (Page 8)
- Gestion de l'adhésion à un Organisme de Gestion Agréé
- Informations de contact et numéro d'adhésion
- Type de service et cotisation annuelle
- Informations sur les avantages fiscaux

### 9. Statut fiscal et social (Page 9)
- Configuration du régime fiscal (Micro-BIC, Réel Simplifié, Réel Normal)
- Option TVA avec numéro intracommunautaire
- Régime social (indépendant, salarié, retraité)
- CFE (Cotisation Foncière des Entreprises)
- Informations et conseils fiscaux

## 🎨 Thèmes

L'application supporte deux thèmes :
- **Mode clair** : Interface classique avec fond blanc
- **Mode nuit** : Interface sombre pour réduire la fatigue oculaire

Pour basculer entre les thèmes, cliquez sur l'icône Lune/Soleil en haut à droite.

## 👤 Compte utilisateur

Le menu utilisateur se trouve en haut à droite :
- Affiche votre nom et email
- Permet de se déconnecter

## ❓ Aide

Le bouton "Aide & FAQ" se trouve en bas du menu latéral gauche.

## 🏗️ Structure technique

### Technologies utilisées
- **React 19** : Framework JavaScript
- **TypeScript** : Typage statique
- **Vite** : Build tool ultra-rapide
- **React Router** : Navigation
- **Tailwind CSS** : Framework CSS utility-first
- **Lucide React** : Bibliothèque d'icônes modernes

### Architecture
```
src/
├── components/
│   ├── layouts/
│   │   └── DashboardLayout.tsx    # Layout principal
│   ├── Header.tsx                  # En-tête avec menu utilisateur
│   ├── Sidebar.tsx                 # Menu latéral
│   ├── PageContainer.tsx           # Container pour les pages
│   └── ProtectedRoute.tsx          # Protection des routes
├── contexts/
│   ├── AuthContext.tsx             # Gestion authentification
│   └── ThemeContext.tsx            # Gestion du thème
├── pages/
│   ├── LoginPage.tsx               # Page de connexion
│   ├── Dashboard.tsx               # Tableau de bord
│   ├── SirenPage.tsx              # Page SIREN
│   ├── LogementsPage.tsx          # Gestion logements
│   ├── UsagePage.tsx              # Usage des logements
│   ├── RecettesPage.tsx           # Recettes
│   ├── DepensesPage.tsx           # Dépenses
│   ├── EmpruntsPage.tsx           # Emprunts
│   ├── OgaPage.tsx                # OGA
│   └── StatutFiscalPage.tsx       # Statut fiscal
├── App.tsx                         # Configuration des routes
└── main.tsx                        # Point d'entrée
```

## 🔐 Persistance des données

Actuellement, les données sont stockées localement dans :
- `localStorage` pour l'utilisateur connecté
- État React pour les données de formulaires

Pour une version production, vous devrez connecter l'application à une API backend.

## 🚀 Build de production

```bash
npm run build
```

Les fichiers optimisés seront générés dans le dossier `dist/`.

## 📝 À faire pour la production

- [ ] Connecter à une vraie API backend
- [ ] Implémenter une vraie authentification avec JWT
- [ ] Ajouter la validation des formulaires
- [ ] Implémenter la persistence en base de données
- [ ] Ajouter des tests unitaires
- [ ] Optimiser les performances
- [ ] Ajouter la gestion d'erreurs avancée
- [ ] Implémenter l'export PDF des données
- [ ] Ajouter des graphiques pour les statistiques

## 🎯 Design moderne

L'application utilise un design moderne avec :
- Dégradés subtils
- Animations de transition fluides
- Responsive design (mobile, tablette, desktop)
- Cartes avec ombres légères
- Boutons avec états hover
- Mode nuit élégant
- Icônes vectorielles de Lucide
- Palette de couleurs cohérente

## 🆘 Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de support.
