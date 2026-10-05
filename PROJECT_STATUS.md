# Build / validation status

- Project generated from the supplied 8-page SRS.
- Python syntax validation: PASS (`python -m compileall -q app tests`).
- Dependency/runtime smoke test: not executable in this sandbox because external package installation is blocked by network/DNS restrictions. The test suite is included for local execution after `pip install -r requirements.txt`.
- Included SRS source: `docs/SRS_SOURCE.pdf`.
- Demo seed users and data are clearly marked for development; replace credentials and sample records before production.
