# LiteLLM Model List

## Model Name Mapping

| Human-Friendly Name | API Model ID (Technical) |
|-------------------|------------------------|
| **OpenAI/GPT Models** | |
| GPT-5 (reasoning, brief) | `gpt-5` |
| GPT-5 Mini | `gpt-5-mini` |
| GPT-5 Nano | `gpt-5-nano` |
| GPT-5 Chat Latest (shows work) | `gpt-5-chat-latest` |
| GPT-4.1 | `gpt-4.1` |
| GPT-4o | `gpt-4o` |
| GPT-4o Mini | `gpt-4o-mini` |
| **Anthropic/Claude Models** | |
| Claude Opus 4.1 | `anthropic/claude-opus-4-1` |
| Claude Opus 4 | `anthropic/claude-opus-4-0` |
| Claude Thinking | `anthropic/claude-opus-4-1` |
| Claude Sonnet 4 | `anthropic/claude-3-5-sonnet-20241022` |
| **Google/Gemini Models** | |
| Gemini 2.5 Pro | `gemini/gemini-2.5-pro` |
| Gemini 2.5 Flash | `gemini/gemini-2.5-flash` |
| Gemini 2.5 Flash Lite | `gemini/gemini-2.5-flash-lite` |
| Gemini 2.5 Flash Image Preview | `gemini/gemini-2.5-flash-image-preview` |
| Gemini 2.5 Flash Preview TTS | `gemini/gemini-2.5-flash-preview-tts` |
| Gemini 2.5 Pro Preview TTS | `gemini/gemini-2.5-pro-preview-tts` |

## Notes

- **GPT models**: Use exact model ID without any prefix
- **Claude models**: Require `anthropic/` prefix for LiteLLM routing
- **Gemini models**: Require `gemini/` prefix for LiteLLM routing

## Current Configuration Location
`/home/administrator/projects/litellm/config.yaml`

## Last Updated
2025-01-11