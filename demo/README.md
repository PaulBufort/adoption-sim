# Demo

Pedagogical Streamlit front end for the simulator. **All data synthetic.**

## Run locally

**One click:** double-click `Launch Demo.command` at the repo root (macOS Finder
opens it in Terminal; Linux: run it). It creates `.venv/` and installs the runtime
dependencies on first use, starts the server, waits for it to report healthy, and
opens http://localhost:8501. Close the window or Ctrl+C to stop. If a demo is
already running it just opens the browser tab. (Port override:
`ADOPTION_SIM_PORT=8765 ./Launch\ Demo.command`.)

Or by hand:

```bash
pip install -r requirements.txt      # from the repo root
streamlit run demo/app.py
```

Serves at http://localhost:8501 — open it manually (the repo ships
`.streamlit/config.toml` with `headless = true`, so no browser auto-opens; that
same setting also suppresses Streamlit's first-run email prompt). First simulation
takes a few seconds; repeated parameter combinations are cached. For liveness
probes use `http://localhost:8501/_stcore/health` (returns `ok`).

## Deploy to Streamlit Community Cloud (free)

1. Push this repository to GitHub (public or with Cloud access).
2. At https://share.streamlit.io → "New app": pick the repo, branch `main`,
   main file path `demo/app.py`.
3. The cloud installs from the root `requirements.txt` (streamlit, networkx, numpy —
   nothing else needed; charts use Streamlit's bundled Altair).
4. Update the demo link in the root `README.md` once the app URL exists.

Sizing note: the free tier runs ~1 vCPU. The demo defaults (1,000 agents ×
5 replicates) take a few seconds there; the sliders cap at 3,000 agents ×
10 replicates, which stays under ~30 s worst case.
