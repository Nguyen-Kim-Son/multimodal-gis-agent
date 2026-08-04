# v1.0.0 release checks

The public package was validated before archiving:

- 22 pytest tests passed.
- `tasks/contextgeo_unique35`: 35 valid tasks.
- `tasks/contextgeo150`: 150 valid task instances.
- Core module imports and mock-adapter construction succeeded.
- `.env`, virtual environments, caches, generated results, and logs were excluded.
- The release archive contains no API keys detected by the packaging checks.

Live API calls were not rerun during packaging because they require user credentials and may incur cost. Use the preflight and cost-estimation scripts before running real-model experiments.
