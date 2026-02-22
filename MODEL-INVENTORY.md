# LiteLLM Model Inventory

**Gateway**: https://litellm.ai-servicers.com (internal: `http://litellm:4000/v1`)
**Last Updated**: 2026-02-21

---

## Model Summary

| # | Model Alias | Provider | Actual Model | Input $/1M | Output $/1M | Tier |
|---|-------------|----------|--------------|-----------|------------|------|
| 1 | `claude-opus-4-6` | Anthropic | claude-opus-4-6 | $5.00 | $25.00 | Premium |
| 2 | `claude-sonnet-4-6` | Anthropic | claude-sonnet-4-6 | $3.00 | $15.00 | Mid |
| 3 | `claude-sonnet-4-5` | Anthropic | claude-sonnet-4-5 | $3.00 | $15.00 | Mid |
| 4 | `claude-haiku-4-5` | Anthropic | claude-haiku-4-5 | $1.00 | $5.00 | Budget |
| 5 | `gemini-3.1-pro` | Google | gemini-3.1-pro-preview | $2.00 | $12.00 | Mid |
| 6 | `gemini-3-flash` | Google | gemini-3-flash-preview | $0.50 | $3.00 | Budget |
| 7 | `gemini-3-flash-mcp` | Google | gemini-3-flash-preview | $0.50 | $3.00 | Budget |
| 8 | `gemini-2.5-pro` | Google | gemini-2.5-pro | $1.25 | $10.00 | Mid |
| 9 | `gemini-2.5-flash` | Google | gemini-2.5-flash | $0.30 | $2.50 | Budget |
| 10 | `gpt-5.2` | OpenAI | gpt-5.2 | $1.75 | $14.00 | Mid |
| 11 | `gpt-5.2-pro` | OpenAI | gpt-5.2-pro | $21.00 | $168.00 | Premium |
| 12 | `gpt-5-mini` | OpenAI | gpt-5-mini | $0.25 | $2.00 | Budget |
| 13 | `o3` | OpenAI | o3 | $2.00 | $8.00 | Mid |

---

## Cost Ranking (Cheapest to Most Expensive by Output)

| Rank | Model | Output $/1M | Best For |
|------|-------|------------|----------|
| 1 | `gpt-5-mini` | $2.00 | High-volume, simple tasks |
| 2 | `gemini-2.5-flash` | $2.50 | Fast, cheap general use |
| 3 | `gemini-3-flash` | $3.00 | Latest Gemini, budget tier |
| 4 | `claude-haiku-4-5` | $5.00 | Quality at low cost |
| 5 | `o3` | $8.00 | Reasoning tasks |
| 6 | `gemini-2.5-pro` | $10.00 | Strong Gemini reasoning |
| 7 | `gemini-3.1-pro` | $12.00 | Latest Gemini flagship |
| 8 | `gpt-5.2` | $14.00 | GPT flagship |
| 9 | `claude-sonnet-4-5` | $15.00 | Claude workhorse |
| 10 | `claude-sonnet-4-6` | $15.00 | Latest Claude mid-tier |
| 11 | `claude-opus-4-6` | $25.00 | Best Claude model |
| 12 | `gpt-5.2-pro` | $168.00 | Maximum GPT capability |

---

## Provider Breakdown

### Anthropic (4 models)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| claude-opus-4-6 | $5.00 | $25.00 | Flagship. Best reasoning + coding |
| claude-sonnet-4-6 | $3.00 | $15.00 | Latest balanced model |
| claude-sonnet-4-5 | $3.00 | $15.00 | Previous gen balanced |
| claude-haiku-4-5 | $1.00 | $5.00 | Fast + cheap. Great for bulk |

**Batch API**: 50% discount on all models
**Cache reads**: 90% discount on input tokens

### Google Gemini (5 models)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| gemini-3.1-pro | $2.00 | $12.00 | Latest flagship (preview) |
| gemini-3-flash | $0.50 | $3.00 | Fast + cheap (preview) |
| gemini-3-flash-mcp | $0.50 | $3.00 | Same as above + MCP postgres access |
| gemini-2.5-pro | $1.25 | $10.00 | Stable pro model |
| gemini-2.5-flash | $0.30 | $2.50 | Cheapest Google model |

**Long context (>200K tokens)**: 2x pricing on Pro models
**Free tier**: Available for Flash models with rate limits

### OpenAI (4 models)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| gpt-5.2 | $1.75 | $14.00 | Current flagship |
| gpt-5.2-pro | $21.00 | $168.00 | Maximum capability, very expensive |
| gpt-5-mini | $0.25 | $2.00 | Cheapest model overall |
| o3 | $2.00 | $8.00 | Reasoning model |

**Cached input**: 90% discount on repeated prompts
**Batch API**: 50% discount for async processing

---

## Usage in Infrastructure

| Use Case | Model | Why |
|----------|-------|-----|
| LiveKit Voice Agent (Claude room) | `claude-sonnet-4-5` | Good quality voice responses |
| LiveKit Voice Agent (ChatGPT room) | `gpt-5-mini` | Cost-effective for voice |
| LiveKit Voice Agent (Gemini room) | `gemini-3-flash` | Fast + cheap for voice |
| aiagentchat (gemini backend) | `gemini-3-flash` | High-volume chat, low cost |
| MCP postgres queries | `gemini-3-flash-mcp` | MCP-enabled with DB access |
| Open WebUI (user choice) | Any | User selects per-conversation |

---

## Estimated Monthly Cost (Typical Usage)

Assuming ~1M input + ~500K output tokens/day across all services:

| Scenario | Model Mix | Est. Monthly Cost |
|----------|-----------|-------------------|
| Budget | All gemini-3-flash | ~$60 |
| Balanced | Mix of flash + sonnet | ~$300 |
| Premium | Heavy opus/gpt-5.2-pro | ~$2,500+ |

---

*Prices sourced from provider pricing pages (Feb 2026). Actual costs may vary with caching, batching, and context length.*
