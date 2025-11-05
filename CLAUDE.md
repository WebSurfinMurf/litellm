# LiteLLM - Unified LLM Gateway

## Project Overview
LiteLLM is a unified API gateway providing access to multiple LLM providers (OpenAI, Anthropic, Google) through a single OpenAI-compatible interface.

## Current Status
- **Status**: ✅ RUNNING
- **Container**: litellm
- **Version**: v1.72.0-stable
- **Port**: 4000
- **Networks**: postgres-net, litellm-net, traefik-net, mcp-net
- **External URL**: https://litellm.ai-servicers.com
- **Last Updated**: 2025-09-30

## Architecture
```
Applications (Open WebUI, MCP Middleware)
    ↓
LiteLLM Gateway (Port 4000)
    ↓
┌────────────────┬──────────────────┬────────────────┐
│   OpenAI API   │  Anthropic API   │  Google AI API │
│  (GPT models)  │ (Claude models)  │ (Gemini models)│
└────────────────┴──────────────────┴────────────────┘
```

## Access Methods
- **Internal API**: http://litellm:4000/v1 (from Docker containers)
- **External API**: https://litellm.ai-servicers.com/v1 (via Traefik)
- **Web UI**: https://litellm.ai-servicers.com/ui
- **Master Key**: sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc

## Available Models

### OpenAI GPT Models (7)
- gpt-5 (reasoning model, brief responses)
- gpt-5-chat-latest (shows detailed work)
- gpt-5-mini, gpt-5-nano
- gpt-4.1, gpt-4o, gpt-4o-mini

### Anthropic Claude Models (4)
- claude-opus-4.1 (latest, most capable)
- claude-opus-4
- claude-thinking (extended reasoning)
- claude-sonnet-4 (fast, balanced)

### Google Gemini Models (8)
- gemini-2.5-pro, gemini-2.5-flash
- gemini-2.5-flash-lite, gemini-2.5-flash-image-preview
- gemini-2.5-flash-preview-tts, gemini-2.5-pro-preview-tts
- gemini-1.5-pro, gemini-1.5-flash (legacy)

## Files & Paths
- **Deploy Script**: `/home/administrator/projects/litellm/docker-compose.yml`
- **Configuration**: `/home/administrator/projects/data/litellm/config/config.yaml`
- **Secrets**: `$HOME/projects/secrets/litellm.env`
- **Temp Directory**: `/home/administrator/projects/data/litellm/tmp/`
- **Model List**: `/home/administrator/projects/litellm/modellist.md`

## Recent Changes

### Session: 2025-11-04
- **Data Location Standardization**: Moved runtime data to centralized location
  - Moved `litellm/config/` to `/projects/data/litellm/config/`
  - Moved `litellm/tmp/` to `/projects/data/litellm/tmp/`
  - Updated docker-compose.yml to use new paths
  - Removed empty `litellm/tools/` directory
  - Follows project data standard: all runtime data in `projects/data/{project}/`

## Configuration

### Environment Variables
Located in `$HOME/projects/secrets/litellm.env`:
- API keys for OpenAI, Anthropic, Google
- Database connection for usage tracking
- Master key for gateway access

### Model Configuration
Located in `/home/administrator/projects/litellm/config/config.yaml`:
- Model routing rules
- Provider settings
- Fallback configurations
- Rate limiting

## Integration Points

### Open WebUI
- **Endpoint**: http://litellm:4000/v1
- **Models**: All 19 models available
- **Authentication**: Master key
- **Status**: ✅ Working

### MCP Middleware
- **Endpoint**: http://litellm:4000/v1
- **Models**: Used for AI tool execution
- **Network**: Connected via litellm-net
- **Status**: ✅ Working

## Common Commands
```bash
# Check status
docker ps | grep litellm

# View logs
docker logs litellm --tail 50

# Restart service
docker restart litellm

# Test API
curl -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  http://localhost:4000/v1/models

# Deploy/redeploy
cd /home/administrator/projects/litellm
docker compose up -d
```

## Health Checks
- **Endpoint**: http://localhost:4000/ui
- **Interval**: 30 seconds
- **Start Period**: 30 seconds
- **Retries**: 3

## Logging
- **Driver**: json-file
- **Max Size**: 20MB per file
- **Max Files**: 5 files retained

## Networks
- **postgres-net**: Database connection for usage tracking
- **litellm-net**: Service communication with Open WebUI, MCP
- **traefik-net**: External HTTPS access via reverse proxy
- **mcp-net**: MCP tool integration

## Database Integration
- **Type**: PostgreSQL
- **Purpose**: Usage tracking, billing, analytics
- **Connection**: Via postgres-net
- **Database**: litellm (if configured)

## Troubleshooting

### Model Not Available
- Check config.yaml for model definition
- Verify API keys in litellm.env
- Check logs: `docker logs litellm --tail 50`

### Connection Issues
- Verify network connectivity
- Check if container is on correct networks
- Test with: `docker exec open-webui ping litellm`

### API Key Errors
- Verify keys in `$HOME/projects/secrets/litellm.env`
- Check provider dashboards for usage limits
- Ensure keys have correct permissions

## Security Notes
- Master key required for all API access
- API keys stored in secrets directory
- No public access without authentication
- HTTPS enforced via Traefik

## Performance Tuning
- Caching enabled for repeated requests
- Connection pooling for database
- Health checks ensure availability
- Multiple provider fallbacks

## Related Documentation
- Model Verification: `/home/administrator/projects/litellm/model-verification.md`
- Open WebUI Integration: `/home/administrator/projects/open-webui/LITELLM_INTEGRATION.md`
- MCP Middleware: `/home/administrator/projects/mcp/middleware/`

---
*Created: 2025-09-30 by Claude*
*Status: Fully operational with 19 models across 3 providers*
