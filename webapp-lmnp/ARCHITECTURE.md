# Architecture de l'application LMNP Manager

## Vue d'ensemble

L'application LMNP Manager est une application web moderne construite avec React et TypeScript, conçue pour gérer les locations meublées non professionnelles (LMNP).

## Stack technique

### Frontend
- **React 19** : Framework JavaScript pour les interfaces utilisateur
- **TypeScript** : Langage typé pour un code plus sûr
- **Vite** : Build tool rapide et moderne
- **React Router v6** : Gestion du routing
- **Tailwind CSS** : Framework CSS utility-first
- **Lucide React** : Icônes modernes et légères

### Outils de développement
- **ESLint** : Linter JavaScript/TypeScript
- **PostCSS** : Transformation CSS
- **Autoprefixer** : Ajout automatique de préfixes CSS

## Architecture des composants

### Structure des dossiers

```
webapp-lmnp/
├── public/                    # Assets statiques
├── src/
│   ├── components/            # Composants réutilisables
│   │   ├── layouts/
│   │   │   └── DashboardLayout.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── PageContainer.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/              # Contexts React
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── pages/                 # Pages de l'application
│   │   ├── LoginPage.tsx
│   │   ├── Dashboard.tsx
│   │   ├── SirenPage.tsx
│   │   ├── LogementsPage.tsx
│   │   ├── UsagePage.tsx
│   │   ├── RecettesPage.tsx
│   │   ├── DepensesPage.tsx
│   │   ├── EmpruntsPage.tsx
│   │   ├── OgaPage.tsx
│   │   └── StatutFiscalPage.tsx
│   ├── App.tsx               # Configuration des routes
│   ├── main.tsx              # Point d'entrée
│   └── index.css             # Styles globaux
├── index.html                # Template HTML
├── package.json              # Dépendances
├── tsconfig.json             # Configuration TypeScript
├── vite.config.ts            # Configuration Vite
└── tailwind.config.js        # Configuration Tailwind
```

## Patterns et principes

### 1. Contexts pour l'état global

Deux contexts principaux :
- `AuthContext` : Gestion de l'authentification et de l'utilisateur
- `ThemeContext` : Gestion du thème (clair/sombre)

```typescript
// Utilisation
const { user, login, logout } = useAuth()
const { isDarkMode, toggleDarkMode } = useTheme()
```

### 2. Routes protégées

Les routes nécessitant une authentification sont protégées par le composant `ProtectedRoute` :

```typescript
<Route path="/" element={
  <ProtectedRoute>
    <DashboardLayout />
  </ProtectedRoute>
}>
```

### 3. Layout composé

Le layout principal (`DashboardLayout`) utilise le pattern Outlet de React Router :

```typescript
<div className="flex">
  <Sidebar />
  <div className="flex-1">
    <Header />
    <main>
      <Outlet /> {/* Les pages enfants s'affichent ici */}
    </main>
  </div>
</div>
```

### 4. Composants de page

Chaque page utilise le composant `PageContainer` pour une cohérence visuelle :

```typescript
<PageContainer title="Titre de la page">
  {/* Contenu */}
</PageContainer>
```

## Gestion de l'état

### État local (useState)

Pour les données de formulaires et l'UI locale :

```typescript
const [formData, setFormData] = useState({
  field1: '',
  field2: ''
})
```

### État global (Context)

Pour les données partagées entre composants :
- Utilisateur connecté
- Thème sélectionné

### Persistence (localStorage)

Données persistées dans le navigateur :
- Utilisateur connecté
- Préférence de thème

## Routing

Structure des routes :

```
/login                    → LoginPage
/                         → DashboardLayout (protected)
  /dashboard              → Dashboard
  /siren                  → SirenPage
  /logements              → LogementsPage
  /usage                  → UsagePage
  /recettes               → RecettesPage
  /depenses               → DepensesPage
  /emprunts               → EmpruntsPage
  /oga                    → OgaPage
  /statut-fiscal          → StatutFiscalPage
```

## Styling

### Tailwind CSS

Utilisation de classes utilitaires :
- `dark:` pour le mode sombre
- Responsive : `md:`, `lg:`, etc.
- Personnalisation dans `tailwind.config.js`

### Thème personnalisé

Couleurs primaires définies :

```javascript
primary: {
  50: '#eff6ff',
  100: '#dbeafe',
  // ...
  900: '#1e3a8a',
}
```

### Mode sombre

Activation automatique avec la classe `dark` sur `<html>` :

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}
```

## Formulaires

### Pattern de gestion

1. État local avec `useState`
2. Handler de soumission
3. Validation (à implémenter)
4. Envoi à l'API (à implémenter)

```typescript
const [formData, setFormData] = useState({...})

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  // Validation
  // API call
}
```

## Navigation

### Menu latéral

Liste des pages avec navigation active :

```typescript
<NavLink to="/dashboard" className={({ isActive }) => 
  isActive ? 'active-class' : 'inactive-class'
}>
```

### Menu utilisateur

Dropdown en haut à droite avec :
- Informations utilisateur
- Bouton de déconnexion

## Authentification

### Simulation actuelle

L'authentification est simulée pour le développement :
- Tout email/mot de passe valide fonctionne
- Token stocké dans localStorage
- Redirection automatique si non authentifié

### Production (à implémenter)

```typescript
// Login avec API
const response = await fetch('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
})

const { token, user } = await response.json()
localStorage.setItem('token', token)
```

## Performance

### Code splitting

React Router charge automatiquement les pages à la demande.

### Optimisations Vite

- Tree shaking automatique
- Minification en production
- Préchargement des modules

### Images

- Utilisation d'icônes SVG (Lucide) pour la légèreté
- Lazy loading pour les images futures

## Accessibilité

- Labels sur tous les inputs
- Aria-labels sur les boutons
- Focus visible
- Navigation au clavier
- Contraste des couleurs (WCAG AA)

## Sécurité

### Recommandations

1. **Authentification JWT** : Implémenter côté backend
2. **HTTPS** : Obligatoire en production
3. **Sanitization** : Valider toutes les entrées utilisateur
4. **CORS** : Configurer correctement
5. **Rate limiting** : Limiter les requêtes API
6. **CSP** : Content Security Policy

## Évolution future

### Phase 2 - Backend

- API REST Node.js/Express ou Python/FastAPI
- Base de données PostgreSQL/MongoDB
- Authentification JWT
- Gestion des fichiers (upload)

### Phase 3 - Fonctionnalités avancées

- Export PDF des déclarations
- Graphiques et statistiques avancées
- Notifications push
- Calendrier de paiements
- Documents attachés
- Multi-propriétaire

### Phase 4 - Mobile

- Progressive Web App (PWA)
- Application mobile React Native
- Notifications mobiles

## Tests

### À implémenter

```bash
# Tests unitaires
npm install --save-dev vitest @testing-library/react

# Tests E2E
npm install --save-dev playwright
```

## Monitoring

### Recommandations

- **Sentry** : Tracking des erreurs
- **Google Analytics** : Analytics
- **Hotjar** : Heatmaps et enregistrements
- **LogRocket** : Session replay

## Documentation API (future)

### Endpoints prévus

```
POST   /api/auth/login
POST   /api/auth/register
GET    /api/user
PUT    /api/user
GET    /api/logements
POST   /api/logements
PUT    /api/logements/:id
DELETE /api/logements/:id
GET    /api/recettes
POST   /api/recettes
GET    /api/depenses
POST   /api/depenses
```

## Contribution

### Convention de code

- Utiliser TypeScript strict
- Suivre les règles ESLint
- Nommer les composants en PascalCase
- Nommer les fonctions en camelCase
- Commenter le code complexe

### Git workflow

```bash
# Créer une branche
git checkout -b feature/nouvelle-fonctionnalité

# Commiter
git commit -m "feat: ajout de la fonctionnalité X"

# Pousser
git push origin feature/nouvelle-fonctionnalité

# Pull Request sur GitHub
```

## Support

Pour toute question sur l'architecture, contactez l'équipe de développement.
