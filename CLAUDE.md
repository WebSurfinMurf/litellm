# Project: LiteLLM

## Overview
- Purpose: Unified LLM API Gateway for Claude, ChatGPT, and Gemini (100+ providers supported)
- URL: https://litellm.ai-servicers.com
- Repository: /home/administrator/projects/litellm
- Created: 2025-01-11
- Updated: 2025-01-11
- Models Configured: 19 (7 GPT, 4 Claude, 8 Gemini)

## Configuration
- Keycloak Client: litellm (pending full SSO integration)
- Environment: /home/administrator/secrets/litellm.env
- Database: litellm_db (PostgreSQL with admin user)
- Container: litellm (ghcr.io/berriai/litellm-database:main-stable)
- Config File: /home/administrator/projects/litellm/config.yaml

## Services & Ports
- Application: Port 4000 (internal)
- External: https://litellm.ai-servicers.com
- Networks: traefik-proxy, postgres-net, redis-net

## Key Features
- Unified OpenAI-compatible API for all LLM providers
- Load balancing with "least-busy" routing strategy
- Automatic fallback chains between models
- Cost tracking and usage analytics (PostgreSQL)
- Rate limiting and quota management
- Virtual key generation for team/user management
- Database persistence for keys, logs, and usage

## Access Credentials
- UI URL: https://litellm.ai-servicers.com/ui
- Admin Username: admin
- Admin Password: LiteLLMAdmin2025!
- Master Key: sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc

## Available Models (19 total)
### OpenAI/ChatGPT (7 models)
- `gpt-5` - GPT-5 (reasoning model, brief responses)
- `gpt-5-chat-latest` - GPT-5 Chat (shows detailed work)
- `gpt-5-mini` - GPT-5 Mini (smaller, faster)
- `gpt-5-nano` - GPT-5 Nano (smallest, fastest)
- `gpt-4.1` - GPT-4.1
- `gpt-4o` - GPT-4 Omni
- `gpt-4o-mini` - GPT-4 Omni Mini

### Anthropic/Claude (4 models)
- `claude-opus-4.1` - Claude Opus 4.1 (latest, most capable)
- `claude-opus-4` - Claude Opus 4
- `claude-thinking` - Claude Opus 4.1 with extended thinking
- `claude-sonnet-4` - Claude 3.5 Sonnet (fast, balanced)

### Google/Gemini (8 models)
- `gemini-2.5-pro` - Gemini 2.5 Pro (advanced reasoning)
- `gemini-2.5-flash` - Gemini 2.5 Flash (fast)
- `gemini-2.5-flash-lite` - Gemini 2.5 Flash Lite (lightweight)
- `gemini-2.5-flash-image-preview` - Gemini 2.5 Flash Image (multimodal)
- `gemini-2.5-flash-preview-tts` - Gemini 2.5 TTS Flash
- `gemini-2.5-pro-preview-tts` - Gemini 2.5 TTS Pro
- `gemini-1.5-pro` - Gemini 1.5 Pro (legacy)
- `gemini-1.5-flash` - Gemini 1.5 Flash (legacy)

## API Usage Examples

### List Available Models
```bash
curl https://litellm.ai-servicers.com/v1/models \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"
```

### Test GPT-5
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

### Test Claude Opus 4.1
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "claude-opus-4.1",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

### Test Gemini 2.5 Pro
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "Say hello"}]
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
- Logs: `docker logs litellm --tail 50`
- Shell: `docker exec -it litellm /bin/sh`
- Database: `PGPASSWORD='Pass123qp' psql -h localhost -p 5432 -U admin -d litellm_db`
- Health check: `curl https://litellm.ai-servicers.com/health -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"`

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