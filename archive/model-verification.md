# Model Verification Prompts

## How to Verify the Correct Model is Executing

### GPT Models (OpenAI)

**Test Prompts:**

1. **Check reasoning tokens (GPT-5 specific)**:
   ```
   "Think step by step: What is 15 * 17?"
   ```
   - GPT-5 will use "reasoning_tokens" in the API response
   - Check response usage: `completion_tokens_details.reasoning_tokens > 0`

2. **Check model capabilities**:
   ```
   "Generate a haiku about quantum computing"
   ```
   - GPT-5: Will complete quickly with high quality
   - GPT-4: Different response patterns

3. **Check API response metadata**:
   - Look at the `"model"` field in the JSON response
   - GPT-5: Returns `"gpt-5-2025-08-07"` or similar
   - GPT-4.1: Returns `"gpt-4.1-2025-04-14"` or similar

### Claude Models (Anthropic)

**Test Prompts:**

1. **Check model behavior**:
   ```
   "Complete this pattern: 🔴🔵🔴🔵🔴"
   ```
   - Claude models handle emoji patterns distinctively

2. **Check thinking capability (Claude Opus 4.1)**:
   ```
   "Explain quantum entanglement in exactly 3 sentences."
   ```
   - Claude Opus 4.1: Precise, follows instructions exactly
   - Other models: May vary in adherence

3. **Check API response**:
   - Look for `"model"` field
   - Claude Opus 4.1: Returns `"claude-opus-4-1-20250805"`
   - Claude Opus 4: Returns `"claude-opus-4-0"`

### Gemini Models (Google)

**Test Prompts:**

1. **Check multimodal understanding**:
   ```
   "List 5 creative uses for a paperclip"
   ```
   - Gemini 2.5 Pro: Comprehensive, creative responses
   - Gemini 2.5 Flash: Faster, more concise

2. **Check reasoning (Gemini 2.5 specific)**:
   ```
   "What's heavier: 1kg of feathers or 1kg of steel? Explain briefly."
   ```
   - Gemini 2.5 models show "reasoning_tokens" in response

3. **Check API response**:
   - Model field shows exact version
   - Example: `"gemini-2.5-pro"` or `"gemini-2.5-flash"`

## Verification Script

```bash
# Test all models with a simple prompt
for model in gpt-5 claude-opus-4.1 gemini-2.5-pro; do
  echo "Testing $model:"
  curl -s https://litellm.ai-servicers.com/v1/chat/completions \
    -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$model\", \"messages\": [{\"role\": \"user\", \"content\": \"Say your name\"}], \"max_tokens\": 30}" | \
    jq -r '.model'
  echo "---"
done
```

## Key Indicators by Model Family

### GPT-5 Family
- **Unique feature**: `reasoning_tokens` in usage details
- **Model IDs**: Include date stamps like `2025-08-07`
- **Response style**: May not self-identify correctly (says GPT-4)

### Claude Family  
- **Unique feature**: Very precise instruction following
- **Model IDs**: `claude-opus-4-1-20250805` format
- **Response style**: Often includes "I'm Claude" in responses

### Gemini Family
- **Unique feature**: `reasoning_tokens` and `text_tokens` split
- **Model IDs**: `gemini-2.5-*` format
- **Response style**: Creative and comprehensive

## Quick Test Command

```bash
# See which model actually responds
curl -s https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "MODEL_NAME", "messages": [{"role": "user", "content": "Hi"}]}' | \
  jq '{model: .model, usage: .usage}'
```

The most reliable verification is checking the API response's `"model"` field and `"usage"` details, not asking the model to self-identify.