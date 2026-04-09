---
name: using-higgsfield-ai
description: Use when generating AI images or videos using the Higgsfield AI / Muapi.ai API
---

# Using Higgsfield AI (via Muapi.ai)

## Overview

This skill covers AI image and video generation using the Open Higgsfield AI project, which connects to the Muapi.ai API. It provides access to 200+ models across four studios without subscription fees.

**Studios available:**
- **Image Studio** — Text-to-image (50+ models) and image-to-image (55+ models)
- **Video Studio** — Text-to-video (40+ models) and image-to-video (60+ models)
- **Lip Sync Studio** — 9 models for animating portraits or syncing audio
- **Cinema Studio** — Professional camera controls (lens, focal length, aperture)

## Setup

### Self-hosted (local development)

```bash
git clone https://github.com/Anil-matcha/Open-Higgsfield-AI.git
cd Open-Higgsfield-AI
npm install
npm run dev
# Access at http://localhost:3000
```

### API key

Obtain a key from [muapi.ai](https://muapi.ai). The app stores it in browser `localStorage` via the `AuthModal` component.

### Environment

```bash
# Required for API calls
MUAPI_API_KEY=your_key_here
MUAPI_BASE_URL=https://api.muapi.ai
```

## API Workflow

The Muapi.ai API follows a **submit → poll** pattern:

### 1. Submit a request

```javascript
const response = await fetch('https://api.muapi.ai/api/v1/{model-endpoint}', {
  method: 'POST',
  headers: {
    'x-api-key': process.env.MUAPI_API_KEY,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'your prompt here',
    // model-specific parameters
  }),
});

const { request_id } = await response.json();
```

### 2. Poll for the result

```javascript
async function pollResult(requestId, maxAttempts = 60, intervalMs = 2000) {
  for (let i = 0; i < maxAttempts; i++) {
    const res = await fetch(
      `https://api.muapi.ai/api/v1/predictions/${requestId}/result`,
      { headers: { 'x-api-key': process.env.MUAPI_API_KEY } }
    );
    const data = await res.json();

    if (data.status === 'completed' || data.status === 'succeeded') {
      // Result URL may be at data.url or data.outputs[0]
      return data.url ?? data.outputs?.[0];
    }
    if (data.status === 'failed') {
      throw new Error(`Generation failed: ${data.error ?? 'unknown error'}`);
    }

    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
  throw new Error('Timed out waiting for result');
}
```

### 3. Upload a file (for image-to-image / image-to-video)

```javascript
async function uploadFile(filePath) {
  const formData = new FormData();
  formData.append('file', fs.createReadStream(filePath));

  const res = await fetch('https://api.muapi.ai/api/v1/upload_file', {
    method: 'POST',
    headers: { 'x-api-key': process.env.MUAPI_API_KEY },
    body: formData,
  });

  const { url } = await res.json();
  return url; // Use this URL as the image input for downstream requests
}
```

## Common Model Endpoints

### Text-to-image

| Model | Endpoint |
|-------|----------|
| Flux Schnell (fast) | `flux-schnell-image` |
| Flux Dev | `flux-dev-image` |
| Flux 2 Pro | `flux-2-pro-image` |
| Midjourney v7 | `midjourney-v7-text-to-image` |
| Google Imagen4 | `google-imagen4-image` |
| GPT-4o Image | `gpt4o-text-to-image` |
| SDXL | `sdxl-image` |

### Text-to-video

| Model | Endpoint |
|-------|----------|
| Wan2.1 | `wan2.1-text-to-video` |
| Wan2.6 | `wan2.6-text-to-video` |
| Kling | `kling-text-to-video` |

### Image-to-video

| Model | Endpoint |
|-------|----------|
| Wan2.1 I2V | `wan2.1-image-to-video` |
| Kling I2V | `kling-image-to-video` |

> **Note:** Check `models_dump.json` in the repo for the full list of model IDs and their exact endpoint paths.

## Complete Example: Text-to-image

```javascript
import fetch from 'node-fetch';

const API_KEY = process.env.MUAPI_API_KEY;
const BASE = 'https://api.muapi.ai';

async function generateImage(prompt, model = 'flux-schnell-image') {
  // Submit
  const submitRes = await fetch(`${BASE}/api/v1/${model}`, {
    method: 'POST',
    headers: { 'x-api-key': API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  const { request_id } = await submitRes.json();

  // Poll
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 2000));
    const pollRes = await fetch(`${BASE}/api/v1/predictions/${request_id}/result`, {
      headers: { 'x-api-key': API_KEY },
    });
    const data = await pollRes.json();
    if (data.status === 'completed' || data.status === 'succeeded') {
      return data.url ?? data.outputs?.[0];
    }
    if (data.status === 'failed') throw new Error(data.error);
  }
  throw new Error('Timeout');
}

const imageUrl = await generateImage('A futuristic cityscape at sunset');
console.log('Generated image:', imageUrl);
```

## Response Normalization

Muapi.ai response structures vary by model. Always check both locations:

```javascript
const resultUrl = data.url ?? data.outputs?.[0];
```

## Error Handling

| Status | Meaning |
|--------|---------|
| `completed` / `succeeded` | Result is ready |
| `failed` | Check `data.error` for details |
| `pending` / `processing` | Keep polling |

## Local Development Proxy

The repo's `vite.config.js` proxies `/api` → `https://api.muapi.ai` to avoid CORS issues during development. When writing server-side code (Node.js), call the API directly without a proxy.

## Project Structure Reference

```
Open-Higgsfield-AI/
├── app/                     # Next.js app
├── packages/studio/         # Shared React component library
├── components/              # UI components (AuthModal, etc.)
├── models_dump.json         # All 200+ model definitions
├── muapi.js                 # API client implementation
└── vite.config.js           # Dev proxy config
```

## Checklist

- [ ] Muapi.ai API key obtained and stored securely (not hardcoded)
- [ ] Using `x-api-key` header (not Bearer token)
- [ ] Submit → poll pattern implemented
- [ ] Handling both `data.url` and `data.outputs[0]` response shapes
- [ ] Polling timeout and error states handled
- [ ] File uploads use multipart form data to `/api/v1/upload_file`
