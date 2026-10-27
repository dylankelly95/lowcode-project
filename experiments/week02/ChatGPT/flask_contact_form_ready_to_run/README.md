# Flask contact form (Flask 3.x)

## Run on macOS
Open Terminal in this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "Flask>=3.0,<4.0"
python app.py
```

Open http://127.0.0.1:5000/contact

Stop the server with Ctrl+C. Only Flask and the Python standard library are used. No data is stored or emailed.
