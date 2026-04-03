# 🔐 Guide d'activation Resend pour Édu-Connect

## Étape 1 : Créer un compte Resend

1. Allez sur **https://resend.com**
2. Cliquez sur "Sign Up"
3. Créez votre compte (email + mot de passe)
4. Vérifiez votre email

## Étape 2 : Obtenir votre API Key

1. Connectez-vous à votre dashboard Resend
2. Dans le menu de gauche, cliquez sur **"API Keys"**
3. Cliquez sur **"Create API Key"**
4. Donnez un nom : `Édu-Connect Production`
5. Permissions : **Full Access** (recommandé) ou **Sending access**
6. Cliquez sur **"Create"**
7. **IMPORTANT** : Copiez immédiatement votre clé API (commence par `re_...`)
   - Elle ne sera plus affichée après !

## Étape 3 : Ajouter la clé dans votre application

### Sur Emergent (Preview/Development)

1. Ouvrir le fichier `/app/backend/.env`
2. Remplacer la ligne :
   ```
   RESEND_API_KEY=
   ```
   Par :
   ```
   RESEND_API_KEY=re_votre_cle_api_ici
   ```

3. (Optionnel) Configurer l'email d'envoi :
   ```
   SENDER_EMAIL=noreply@votre-domaine.cd
   SENDER_NAME=Édu-Connect MINEPST
   ```
   
   **Note** : En mode test Resend, utilisez `onboarding@resend.dev`

4. Redémarrer le backend :
   ```bash
   sudo supervisorctl restart backend
   ```

### Sur Emergent (Production déployée)

Si vous déployez sur Emergent :
1. Allez dans les **Settings** de votre projet
2. Section **Environment Variables**
3. Ajoutez :
   - `RESEND_API_KEY` = `re_votre_cle_api_ici`
   - `SENDER_EMAIL` = `noreply@votre-domaine.cd`
   - `SENDER_NAME` = `Édu-Connect MINEPST`

## Étape 4 : Vérifier la configuration de votre domaine

### Pour envoyer depuis votre propre domaine (recommandé en production)

1. Dans Resend Dashboard → **Domains**
2. Cliquez sur **"Add Domain"**
3. Entrez votre domaine : `educonnect.gouv.cd` (exemple)
4. Suivez les instructions pour ajouter les enregistrements DNS :
   - **SPF** : `v=spf1 include:resend.com ~all`
   - **DKIM** : Clé fournie par Resend
   - **DMARC** : Recommandé pour la délivrabilité

5. Attendez la vérification (quelques minutes à quelques heures)

6. Une fois vérifié, mettez à jour `.env` :
   ```
   SENDER_EMAIL=noreply@educonnect.gouv.cd
   ```

## Étape 5 : Tester l'envoi d'emails

### Test via API directe

```bash
API_URL="https://edu-connect-drc.preview.emergentagent.com"

# Se connecter
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"ministre@educonnect.gouv.cd","password":"Ministre2026!"}' | \
  jq -r '.access_token')

# Créer un document (déclenche un email au destinataire)
curl -X POST "$API_URL/api/documents/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "titre=Test Email Resend" \
  -F "type_document=administratif" \
  -F "destinataire_final_id=sg_001" \
  -F "destinataire_final_nom=Secrétaire Général"
```

### Vérifier les logs

```bash
# Vérifier que l'email a été envoyé
tail -100 /var/log/supervisor/backend.out.log | grep "Email sent"
```

Si vous voyez :
- ✅ `Email sent successfully to xxx@xxx.com: ****` → Resend fonctionne !
- 🔶 `RESEND_API_KEY not configured - Email NOT sent (mock mode)` → Clé manquante

## Étape 6 : Mode test vs Production

### Mode Test (gratuit, 100 emails/jour)
- Emails envoyés uniquement aux adresses vérifiées
- Parfait pour le développement
- Utilisez `onboarding@resend.dev` comme expéditeur

### Mode Production (payant, dès 1$/mois)
- Envoi illimité à n'importe quelle adresse
- Domaine personnalisé vérifié requis
- Métriques et analytics

## Tarification Resend

- **Gratuit** : 100 emails/jour, 1 domaine
- **Pro** : 1$/mois pour 10 000 emails
- **Business** : Sur devis

## Troubleshooting

### Erreur : "Invalid API key"
- Vérifiez que la clé commence par `re_`
- Vérifiez qu'il n'y a pas d'espaces
- Redémarrez le backend après modification

### Emails non reçus
- Vérifiez les spams
- En mode test : vérifiez que l'email du destinataire est vérifié dans Resend
- Vérifiez les logs backend

### Erreur : "Domain not verified"
- Attendez la vérification DNS (peut prendre 24-48h)
- Utilisez `onboarding@resend.dev` en attendant

## Support

- Documentation Resend : https://resend.com/docs
- Dashboard : https://resend.com/dashboard
- Support : support@resend.com

---

**Une fois configuré, tous vos emails GED seront automatiquement envoyés via Resend ! 🎉**
