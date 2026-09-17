# Standalone verification evidence

Checked at 2026-09-17T05:01:48.625115+00:00. These results come from commands executed inside this repository after export.

Runtime versions: Python 3.14.7; Node.js v25.9.0.

Standalone release verification: **PASS**. All recorded commands passed.

| Check | Observed result |
|---|---|
| Python unit and integration tests | 80 discovered; 78 executed; 2 skipped |
| Statement coverage | 547/555 (98.56%) |
| Branch coverage | 253/262 (96.56%) |
| Frontend tests | 31 discovered; 25 executed; 6 skipped |
| Built application discovery | governed_analytics |
| Installed project directories | governed_analytics |
| Installed UI templates | governed_analytics |
| Missing README targets | [] |
| Default input | Executed through the repository CLI; saved in `examples/report.json` |

Reproduce from the repository root:

```sh
python -m pip install -r requirements-dev.txt
python -m coverage run -m unittest discover -s tests -v
python -m coverage report --fail-under=90
python -m portfolio build --output dist
node --test tests/frontend.test.mjs
```

Application source SHA-256: `06c758cdb068871df88be8b101e83aa0f99537a99cab66af0f8b90f760c79ae4`.

Coverage includes this application and its shared Python runtime. Skipped tests exercise capabilities belonging to applications absent from this standalone repository. Provider transport tests use controlled doubles; these counts are not live-model accuracy measurements. The frontend suite exercises rendering, escaping, input binding and asynchronous state with controlled DOM/worker harnesses; it is not an exhaustive visual, accessibility or browser compatibility audit. Coverage measures executed code paths and does not establish semantic correctness.

See the solution-specific independent review linked in the README and the [shared runtime review](INDEPENDENT_RUNTIME_REVIEW.md) for review findings, repairs and limits.
