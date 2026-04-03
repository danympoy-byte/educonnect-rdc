#!/bin/bash
# Script de vérification post-déploiement pour edu-connect-rdc.net

echo "🔍 Vérification de la configuration edu-connect-rdc.net"
echo "========================================================"
echo ""

DOMAIN="edu-connect-rdc.net"
HTTPS_URL="https://$DOMAIN"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 1. Vérification de la résolution DNS..."
if host $DOMAIN > /dev/null 2>&1; then
    IP=$(host $DOMAIN | grep "has address" | awk '{print $4}' | head -1)
    if [ ! -z "$IP" ]; then
        echo -e "${GREEN}✅ DNS résolu : $DOMAIN -> $IP${NC}"
    else
        CNAME=$(host $DOMAIN | grep "is an alias" | awk '{print $6}' | head -1)
        if [ ! -z "$CNAME" ]; then
            echo -e "${GREEN}✅ DNS résolu : $DOMAIN -> $CNAME${NC}"
        else
            echo -e "${YELLOW}⚠️  DNS résolu mais format inattendu${NC}"
        fi
    fi
else
    echo -e "${RED}❌ DNS non résolu - Le domaine n'est pas encore propagé${NC}"
    echo "   Attendez 15-30 minutes et réessayez"
    echo "   Vérifiez sur https://dnschecker.org"
    exit 1
fi

echo ""
echo "🌐 2. Vérification de l'accessibilité HTTPS..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L $HTTPS_URL/login 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Site accessible : $HTTPS_URL (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}❌ Impossible de se connecter au site${NC}"
    echo "   Le site n'est pas encore déployé ou le DNS n'est pas propagé"
    exit 1
else
    echo -e "${YELLOW}⚠️  Site répond mais avec code HTTP $HTTP_CODE${NC}"
fi

echo ""
echo "🔒 3. Vérification du certificat SSL..."
SSL_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Certificat SSL valide${NC}"
    echo "$SSL_INFO" | sed 's/^/   /'
else
    echo -e "${RED}❌ Pas de certificat SSL ou certificat invalide${NC}"
    echo "   Attendez 10-15 minutes après la propagation DNS"
    echo "   Emergent génère automatiquement le certificat"
fi

echo ""
echo "🔧 4. Vérification de l'API Backend..."
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $HTTPS_URL/api/health 2>/dev/null)

if [ "$API_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ API Backend accessible (HTTP $API_HEALTH)${NC}"
elif [ "$API_HEALTH" = "000" ]; then
    echo -e "${YELLOW}⚠️  API Backend non accessible (peut être normal si endpoint /health n'existe pas)${NC}"
else
    echo -e "${YELLOW}⚠️  API Backend répond avec code HTTP $API_HEALTH${NC}"
fi

echo ""
echo "📱 5. Test de connexion Admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$HTTPS_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@educonnect.cd","password":"Admin@EduConnect2026!"}' 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Connexion admin fonctionnelle${NC}"
    echo "   Compte : admin@educonnect.cd"
else
    echo -e "${RED}❌ Connexion admin échouée${NC}"
    echo "   Vérifiez que les comptes admin sont bien créés"
    echo "   Réponse API : $LOGIN_RESPONSE"
fi

echo ""
echo "========================================================"
echo "✅ Vérification terminée !"
echo ""
echo "🌐 URLs de test :"
echo "   - Login : $HTTPS_URL/login"
echo "   - Dashboard : $HTTPS_URL/dashboard"
echo ""
echo "🔐 Identifiants admin :"
echo "   - Email : admin@educonnect.cd"
echo "   - Mot de passe : Admin@EduConnect2026!"
echo ""
echo "📊 Pour vérifier la propagation DNS globale :"
echo "   https://dnschecker.org/#A/$DOMAIN"
