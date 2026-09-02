"""Exercise the running API, worker, and every generated image output."""
from __future__ import annotations

import io
import time

import httpx
from PIL import Image, ImageDraw


BASE = "http://127.0.0.1:8000"
print("HEALTH", httpx.get(f"{BASE}/api/health").json())
print("FRONTEND", httpx.get("http://127.0.0.1:3000").status_code)
job = httpx.post(f"{BASE}/api/jobs", json={"name": "End-to-end verification"}).json()

source = Image.new("RGB", (360, 280), (245, 245, 240))
draw = ImageDraw.Draw(source)
draw.rounded_rectangle((80, 35, 280, 250), radius=26, fill=(38, 112, 79), outline=(20, 70, 48), width=4)
draw.ellipse((120, 70, 240, 190), fill=(201, 244, 91))
buffer = io.BytesIO()
source.save(buffer, "PNG")

upload = httpx.post(
    f"{BASE}/api/jobs/{job['id']}/images",
    files={"files": ("e2e-product.png", buffer.getvalue(), "application/octet-stream")},
)
upload.raise_for_status()
asset = upload.json()["uploaded"][0]
print("UPLOAD", upload.status_code, asset["mime_type"])
httpx.post(f"{BASE}/api/jobs/{job['id']}/process").raise_for_status()

started = time.time()
status = "QUEUED"
ticks = 0
while status in {"UPLOADED", "QUEUED", "PROCESSING"} and time.time() - started < 300:
    time.sleep(1)
    status = httpx.get(f"{BASE}/api/images/{asset['id']}").json()["status"]
    ticks += 1
    if ticks % 5 == 0:
        print("STATUS", status, int(time.time() - started), "s", flush=True)
print("FINAL", status)
assert status in {"COMPLETED", "NEEDS_REVIEW"}, status

for variant in ("mask", "transparent", "white.png", "white.jpg", "thumbnail"):
    response = httpx.get(f"{BASE}/api/images/{asset['id']}/{variant}")
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as result:
        result.verify()
        print("OUTPUT", variant, len(response.content), result.format, result.size)
print("E2E_OK", job["id"], asset["id"])

