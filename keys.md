# Keys - unde le pui si cum le generezi

1. Pentru POSTGRES_PASSWORD rulezi:
openssl rand -hex 24
Pui valoarea in Dockploy la:
- doisense-app
- doisense-monitoring
Regula: trebuie sa fie IDENTICA in ambele.

2. Pentru MINIO_ROOT_PASSWORD rulezi:
openssl rand -hex 24
Pui valoarea in Dockploy la:
- doisense-app

3. Pentru GRAFANA_ADMIN_PASSWORD rulezi:
openssl rand -hex 16
Pui valoarea in Dockploy la:
- doisense-monitoring

4. Pentru SECRET_KEY rulezi:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
Pui valoarea in Dockploy la:
- doisense-app

5. Pentru STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET si Stripe Price IDs:
- le iei din Stripe Dashboard
- le pui in Dockploy la:
  - doisense-app
- setezi si variabilele de planuri:
  - STRIPE_PRICE_ID_BASIC
  - STRIPE_PRICE_ID_PREMIUM
  - STRIPE_PRICE_ID_VIP
  - STRIPE_PRICE_ID_BASIC_YEARLY
  - STRIPE_PRICE_ID_PREMIUM_YEARLY
  - STRIPE_PRICE_ID_VIP_YEARLY
- pentru productie setezi explicit:
  - ALLOW_DB_STRIPE_SECRETS=false

6. Pentru OPENAI_API_KEY si ANTHROPIC_API_KEY:
- le iei din OpenAI / Anthropic
- le pui in Dockploy la:
  - doisense-app

Reguli importante:
- Nu refolosi aceeasi valoare pentru toate cheile.
- POSTGRES_PASSWORD trebuie identic in doisense-app si doisense-monitoring.
- Dupa orice schimbare de env, rulezi redeploy pe serviciul afectat.
