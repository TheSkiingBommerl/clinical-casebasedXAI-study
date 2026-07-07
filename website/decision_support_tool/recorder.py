"""
This code was created by Sonnet 4.6
"""

import datetime
import os
from pathlib import Path

import dotenv
from flask import Flask, Response, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

current_path = Path(__file__)
with open(current_path.parent / "components" / "html" / "recorder.html") as f:
    RECORDER_HTML = f.read()


@app.route("/recorder")
def recorder():
    challenge = request.args.get("challenge", "none")
    if challenge != os.environ["FLOCHALLENGE"]:
        abort(401)
    return Response(RECORDER_HTML, mimetype="text/html")


@app.route("/upload", methods=["POST"])
def upload():
    user = request.args.get("user", "unknown").replace("@", "_").replace(".", "_")

    challenge = request.args.get("challenge", "none")
    if challenge != os.environ["FLOCHALLENGE"]:
        abort(401)

    chunk = int(request.args.get("chunk", 0))
    ext = request.args.get("ext", "webm")  # client sends ext
    root = Path(os.environ["FLO_RESULTS"])
    folder = root / "recordings" / user / "chunks"
    folder.mkdir(exist_ok=True, parents=True)

    with open(folder / f"chunk_{chunk:05d}.{ext}", "wb") as f:
        f.write(request.data)
    return "ok"


@app.route("/stop", methods=["POST"])
def stop():
    challenge = request.args.get("challenge", "none")
    if challenge != os.environ["FLOCHALLENGE"]:
        abort(401)

    user = request.args.get("user", "unknown").replace("@", "_").replace(".", "_")

    root = Path(os.environ["FLO_RESULTS"])
    folder = root / "recordings" / user / "chunks"

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if not os.path.exists(folder):
        return "no chunks"

    chunks = sorted(os.listdir(folder))
    if not chunks:
        return "empty"

    # Detect extension from first chunk (mp4 on Edge, webm on Chrome/Firefox)
    first = chunks[0]
    ext = ".mp4" if first.endswith(".mp4") else ".webm"
    output_path = root / "recordings" / user / f"{user}_{now}{ext}"

    with open(output_path, "wb") as out:
        for chunk_file in chunks:
            path = folder / chunk_file
            with open(path, "rb") as f:
                out.write(f.read())
            os.remove(path)

    os.rmdir(folder)
    return "ok"


stop_signals = set()


@app.route("/signal-stop", methods=["POST"])
def signal_stop():
    challenge = request.args.get("challenge", "none")
    if challenge != os.environ["FLOCHALLENGE"]:
        abort(401)
    user = request.args.get("user", "unknown")
    stop_signals.add(user)
    return "ok"


@app.route("/check-stop", methods=["GET"])
def check_stop():
    challenge = request.args.get("challenge", "none")
    if challenge != os.environ["FLOCHALLENGE"]:
        abort(401)
    user = request.args.get("user", "unknown")
    if user in stop_signals:
        stop_signals.discard(user)
        return "stop"
    return "ok"


if __name__ == "__main__":
    dotenv.load_dotenv()
    from waitress import serve
    serve(app, host="0.0.0.0", port=5050)
