# LiteLLM Secure Deployment Guide

## Overview
This deployment uses Docker network isolation to secure MCP services. The MCP proxy is only accessible to LiteLLM via the `litellm-net` Docker network, preventing unauthorized access from the host.

## Architecture

```
Internet → Traefik → LiteLLM ← litellm-net → MCP Proxy → MCP Services
                         ↑
                    (No host access)
```

## Security Features
- ✅ MCP proxy NOT exposed on host ports
- ✅ Only LiteLLM container can access MCP services
- ✅ Role-based API keys control who gets filesystem access
- ✅ Network isolation prevents port scanning attacks

## Deployment Steps

### 1. Deploy MCP Proxy (Network Isolated)
```bash
cd /home/administrator/projects/mcp/proxy-sse
./deploy.sh
```

This will:
- Create `litellm-net` Docker network
- Deploy MCP proxy WITHOUT port 8585 exposure
- Connect to postgres-net for database access
- Show internal URLs for configuration

### 2. Deploy LiteLLM
```bash
cd /home/administrator/projects/litellm
./deploy-secure.sh
```

This will:
- Connect LiteLLM to `litellm-net` network
- Connect to other required networks (postgres, redis, etc.)
- Deploy with Traefik for HTTPS access
- Show configuration details

### 3. Update MCP URLs in LiteLLM UI

Access: https://litellm.ai-servicers.com/ui
Login: admin / LiteLLMAdmin2025!

Update each MCP server URL from:
- OLD: `http://localhost:8585/servers/{service}/sse`
- NEW: `http://mcp-proxy-sse:8080/servers/{service}/sse`

Services to update:
1. filesystem → `http://mcp-proxy-sse:8080/servers/filesystem/sse`
2. postgres → `http://mcp-proxy-sse:8080/servers/postgres/sse`
3. fetch → `http://mcp-proxy-sse:8080/servers/fetch/sse`
4. monitoring → `http://mcp-proxy-sse:8080/servers/monitoring/sse`
5. n8n → `http://mcp-proxy-sse:8080/servers/n8n/sse`
6. playwright → `http://mcp-proxy-sse:8080/servers/playwright/sse`
7. timescaledb → `http://mcp-proxy-sse:8080/servers/timescaledb/sse`

### 4. Test Security

Verify MCP proxy is NOT accessible from host:
```bash
# This should FAIL (connection refused)
curl http://localhost:8585/servers/filesystem/sse

# This should also FAIL
nc -zv localhost 8585
```

Test API keys work:
```bash
# Admin key (has filesystem access)
curl -X POST https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer sk-pFgey4HPR9qDvyT-N_7yVQ" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "test"}]}'

# Dev key (no filesystem access)
curl -X POST https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer sk-nzq2BIYVoVUpz5csqr69xA" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "test"}]}'
```

## Rollback Plan

If issues occur:
```bash
# Stop new deployment
cd /home/administrator/projects/litellm
docker-compose down

cd /home/administrator/projects/mcp/proxy-sse
docker-compose down

# Restore old deployment (if needed)
# Re-run original deploy scripts with port exposure
```

## Monitoring

Check container status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Networks}}"
```

View logs:
```bash
docker logs litellm --tail 50
docker logs mcp-proxy-sse --tail 50
```

Test internal connectivity:
```bash
# From LiteLLM container
docker exec litellm curl -s http://mcp-proxy-sse:8080/servers/filesystem/sse
```

## Network Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Internet  │────▶│   Traefik    │────▶│   LiteLLM    │
└─────────────┘     └──────────────┘     └──────┬───────┘
                    (traefik-proxy)              │
                                          (litellm-net)
                                                 │
                    ┌──────────────┐     ┌──────▼───────┐
                    │  PostgreSQL  │◀────│  MCP Proxy   │
                    └──────────────┘     └──────────────┘
                     (postgres-net)        (No host port)
```

## Important Notes

1. **MCP URLs must use container name**: `mcp-proxy-sse` not `localhost`
2. **Port 8585 is gone**: This is intentional for security
3. **Network names matter**: Both containers must be on `litellm-net`
4. **API keys control access**: Admin vs Developer permissions

## Troubleshooting

### LiteLLM can't reach MCP
- Check both containers are on litellm-net: `docker network inspect litellm-net`
- Test from LiteLLM container: `docker exec litellm ping mcp-proxy-sse`

### MCP services not working
- Check proxy logs: `docker logs mcp-proxy-sse`
- Verify services in config: `docker exec mcp-proxy-sse cat /app/servers.json`

### Port 8585 still exposed
- Stop old container: `docker stop mcp-proxy-sse`
- Check nothing on 8585: `lsof -i :8585`
- Redeploy with new docker-compose

---
*Created: 2025-09-07*
*Security: Network Isolated*
*Author: Claude*