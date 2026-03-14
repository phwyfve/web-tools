# Déploiement de l'application LMNP Manager

## Options de déploiement

### 1. Vercel (Recommandé)

Vercel est idéal pour les applications React/Vite.

```bash
# Installation de Vercel CLI
npm i -g vercel

# Déploiement
vercel
```

Configuration automatique pour Vite. Aucune configuration supplémentaire nécessaire.

### 2. Netlify

```bash
# Installation de Netlify CLI
npm i -g netlify-cli

# Build
npm run build

# Déploiement
netlify deploy --prod --dir=dist
```

### 3. GitHub Pages

Ajoutez dans `vite.config.ts` :
```typescript
export default defineConfig({
  base: '/nom-du-repo/',
  // ... reste de la config
})
```

Dans `package.json`, ajoutez :
```json
{
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

Installez gh-pages :
```bash
npm install --save-dev gh-pages
npm run deploy
```

### 4. Docker

Créez un `Dockerfile` :
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build et run :
```bash
docker build -t lmnp-app .
docker run -p 80:80 lmnp-app
```

### 5. Serveur classique (Apache/Nginx)

1. Build :
```bash
npm run build
```

2. Copiez le contenu de `dist/` sur votre serveur

3. Configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    root /var/www/lmnp-app/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

4. Configuration Apache (.htaccess) :
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

## Variables d'environnement

Pour la production, créez un fichier `.env.production` :

```env
VITE_API_URL=https://api.votre-domaine.com
VITE_APP_NAME=LMNP Manager
```

Utilisez-les dans le code :
```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

## Optimisations pour la production

### 1. Analyse du bundle

```bash
npm run build -- --mode analyze
```

### 2. Compression

Activez la compression gzip/brotli sur votre serveur.

### 3. CDN

Utilisez un CDN comme Cloudflare pour servir les assets statiques.

### 4. Service Worker

Ajoutez un service worker pour le cache et le mode offline.

## Checklist avant déploiement

- [ ] Toutes les fonctionnalités testées
- [ ] Mode production testé localement (`npm run build && npm run preview`)
- [ ] Variables d'environnement configurées
- [ ] Analytics configuré (Google Analytics, Plausible, etc.)
- [ ] Erreurs de console corrigées
- [ ] Performance testée (Lighthouse)
- [ ] Responsive testé sur mobile/tablette
- [ ] SEO optimisé (meta tags, sitemap)
- [ ] HTTPS configuré
- [ ] Backup des données configuré
- [ ] Monitoring configuré (Sentry, LogRocket, etc.)

## Monitoring

### Sentry pour les erreurs

```bash
npm install @sentry/react
```

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "votre-dsn",
  environment: "production",
});
```

### Google Analytics

```typescript
// Dans index.html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## SSL/HTTPS

Utilisez Let's Encrypt pour un certificat SSL gratuit :

```bash
sudo certbot --nginx -d votre-domaine.com
```

## Backup

Mettez en place une stratégie de backup automatique :
- Base de données : backup quotidien
- Fichiers : backup hebdomadaire
- Stockage distant (S3, Backblaze, etc.)

## Support multi-tenant

Pour supporter plusieurs utilisateurs/entreprises, ajoutez :
- Authentification JWT avec backend
- Base de données par utilisateur ou multi-tenant
- API REST ou GraphQL
- Rate limiting
- Gestion des permissions

## Performance

Objectifs Lighthouse :
- Performance : > 90
- Accessibility : > 90
- Best Practices : > 90
- SEO : > 90

## Coûts estimés

### Option gratuite
- Vercel/Netlify free tier : 0€
- GitHub Pages : 0€

### Option payante (petite/moyenne entreprise)
- Vercel Pro : ~20€/mois
- DigitalOcean Droplet : ~5-10€/mois
- Domaine : ~10€/an
- SSL : Gratuit (Let's Encrypt)
- Backend API : ~20-50€/mois (selon usage)
- Base de données : ~10-30€/mois

Total estimé : 40-100€/mois pour une solution professionnelle.
