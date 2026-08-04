# Model selection rationale

The selected set is designed to compare different model families and capabilities rather than multiple near-identical variants.

| Model | Role |
|---|---|
| GPT-OSS-20B Free | Open-weight/free baseline |
| Gemma 4 26B A4B Free | Efficient instruction/MoE baseline |
| GPT-5 Mini | Compact proprietary reasoning baseline |
| Gemini 2.5 Flash | Reasoning and high-throughput baseline |
| Qwen3 Coder | Coding, workflow, and tool-use baseline |
| Claude Sonnet 4 | Optional premium strong baseline |

Free endpoints may become unavailable. Availability is checked immediately before each run and saved in `reports/openrouter_preflight.csv`.
