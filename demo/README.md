# Demo

Pedagogical Streamlit front end for the simulator. **All data synthetic.**

## Run locally

```bash
pip install -r requirements.txt      # from the repo root
streamlit run demo/app.py
```

Opens at http://localhost:8501. First simulation takes a few seconds; repeated
parameter combinations are cached.

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
