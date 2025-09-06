# Project: Litellm

## Overview
- Purpose: AI Gateway/Proxy for unified access to 100+ LLM providers (OpenAI, Anthropic, Gemini, etc.)
- URL: https://litellm.ai-servicers.com
- Repository: /home/administrator/projects/litellm
- Created: 2025-09-06

## Configuration
- Keycloak Client: litellm (pending full SSO integration)
- Environment: /home/administrator/secrets/litellm.env
- Database: litellm_db (PostgreSQL)
- Container: litellm

## Services & Ports
- Application: Port 4000 (internal)
- External: https://litellm.ai-servicers.com

## Key Features
- Unified API endpoint for multiple LLM providers
- Load balancing and fallback between models
- Cost tracking and usage analytics
- Rate limiting and quota management
- Model response caching (via Redis)
- Database persistence for keys and logs

## Access Credentials
- UI URL: https://litellm.ai-servicers.com/ui/
- Username: admin
- Password: TeKhAp2kKjU5tQFJ7ZlFdw==
- Master Key: sk-1234

## API Usage
```bash
# Test with curl
curl https://litellm.ai-servicers.com/v1/models \
  -H "Authorization: Bearer sk-1234"

# OpenAI-compatible endpoint
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Deployment
```bash
cd /home/administrator/projects/litellm
./deploy.sh
```

## Configuration Management
- Add LLM provider API keys via UI or environment variables
- Configure model routing and fallbacks in UI
- Set rate limits and quotas per key

## Troubleshooting
- Logs: `docker logs litellm`
- Shell: `docker exec -it litellm /bin/sh`
- Database: `PGPASSWORD='LitellmPass2025' psql -h localhost -p 5432 -U litellm_user -d litellm_db`
- Health check: `curl https://litellm.ai-servicers.com/health`

## Network Connections
- traefik-proxy: For HTTPS ingress
- postgres-net: Database access
- redis-net: Caching layer
- keycloak-net: Future SSO integration

## Next Steps
1. Configure LLM provider API keys in UI
2. Set up team/user management
3. Configure rate limiting and quotas
4. Integrate with Keycloak for full SSO
5. Set up monitoring and alerting
6. Configure model routing rules

## Documentation
- Official Docs: https://docs.litellm.ai/
- API Reference: https://litellm.ai-servicers.com/docs
- GitHub: https://github.com/BerriAI/litellm