# Test suite

Tests are grouped by the responsibility they protect:

- `contracts/`: public-surface and removed-compatibility contracts.
- `core/`: review, routing, lifecycle, prompting, and shared state behavior.
- `hosts/`: Claude and Codex adapter, hook, and delivery integration.
- `packaging/`: installation, migration, doctor, and plugin inventory.
- `providers/`: reviewer-provider transports and validation.
- `structure/`: repository test-layout guardrails.

Run the complete suite from the repository root:

```powershell
python -m unittest discover -v
```
