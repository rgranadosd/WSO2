# WSO2 APIM Load Testing Tool

Async load-testing tool for WSO2 APIM APIs with OAuth2, random prompts, batch execution with configurable gaps, and real-time progress.

## Features

- OAuth2 client credentials flow (auto token fetch)
- Random question selection from `config.yaml`
- Simple load test: one batch of N requests
- Batch mode with gaps and total duration
- Live progress bars (sent vs completed)
- Detailed stats: latencies, actual RPS, success/fail
- RPS throttling with accurate pacing

## Setup

1) Configure `config.yaml` with your credentials and endpoint:

```yaml
oauth2:
  token_url: "https://apim-next.apis.coach:9450/oauth2/token"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  scope: ""

api:
  endpoint: "https://apim-next.apis.coach:8250/your-api/chat/completions"
  model: "gpt-4o-mini"
  max_tokens: 200     # 50 often truncates; 200+ recommended
  temperature: 0.2
  questions:
    - "Your first question"
    - "Your second question"

http:
  verify_ssl: false
```

2) Bootstrap environment and dependencies:

```bash
./run.sh
```

## Usage

### Single Request (quick connectivity test)

```bash
./run.sh
```
Shows the full request (headers + payload) and prints the response.

### Load Test (single batch)

```bash
# 10 requests (default)
./run.sh load

# 20 requests at 10 RPS
./run.sh load --count 20

# 50 requests at 5 RPS
./run.sh load --rps 5 --count 50
```

### Batch Mode (batches with gaps and total time)

```bash
# 15 requests per batch, 30s gap, 5 minutes total
./run.sh load --count 15 --gap 30 --time 300

# 10 requests per batch at 8 RPS, 20s gap, 2 minutes total
./run.sh load --rps 8 --count 10 --gap 20 --time 120
```

## Parameters

- `--rps` (int, default 10): target requests per second
- `--count` (int, default 10): requests per batch
- `--gap` (int, optional): seconds between batches
- `--time` (int, optional): total duration in seconds (required with `--gap`)

If `--gap` is provided without `--time`, the tool defaults to `--time 300` and prints a warning.

## Outputs

- Progress bars:
  - "Enviando" (blue): requests scheduled/sent
  - "Resultados" (green): requests completed
- Summary: total time, target vs actual RPS, success/fail ratio
- Latency metrics: average, P50, P95, P99
- Error breakdown: HTTP codes, timeouts, SSL/connection errors

## Common Issues

- `finish_reason: "length"`: Increase `max_tokens` to 200+ to avoid truncation
- HTTP 446 (content moderation): Adjust input questions to avoid blocked content
- TIMEOUT (60s): Backend not responding or network issues

## File Structure

```
attack/
├── app.py            # Single request tester
├── load_test.py      # Async load test (simple + batches)
├── config.yaml       # OAuth2 & API config + questions
├── run.sh            # Bootstrap + runner
├── sustained_load.sh # Convenience script for 5-min sustained test
└── README_EN.md      # This document
```

## Dependencies

- requests
- aiohttp
- PyYAML
- tqdm

Installed automatically via `./run.sh`.
