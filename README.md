# Smart Emergency Vehicle Priority System

This is a software-only prototype for a cloud-based emergency vehicle signal priority system.

## What it shows

- Ambulance or fire vehicle GPS updates every 5 seconds
- Cloud server receives and processes the GPS data
- Nearest traffic signal is identified
- If the vehicle is within 1 km, a priority command is generated
- Dashboard shows which signal should change

## Files

- `app.py` -> Flask cloud server and decision logic
- `ambulance.py` -> emergency vehicle GPS simulator
- `templates/index.html` -> dashboard page
- `static/style.css` -> dashboard styling
- `static/script.js` -> live dashboard logic

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`

## Optional GPS simulation from terminal

```bash
python ambulance.py
```
