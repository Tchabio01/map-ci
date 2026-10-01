"""iss_timelapse.py - Timelapse ISS avec ffmpeg"""
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

TL_DIR = Path.home() / "mapci_timelapse"


def has_ffmpeg():
    return shutil.which("ffmpeg") is not None


def nouvelle_session(nom=None):
    nom = nom or datetime.now().strftime("session_%Y%m%d_%H%M%S")
    d = TL_DIR / nom
    d.mkdir(parents=True, exist_ok=True)
    return d


def capture_frame(session_dir, image_bytes=None, source_url=None):
    import requests
    session_dir = Path(session_dir)
    n = len(list(session_dir.glob("frame_*.png"))) + 1
    fname = session_dir / ("frame_" + str(n).zfill(5) + ".png")

    if image_bytes:
        fname.write_bytes(image_bytes)
    elif source_url:
        r = requests.get(source_url, timeout=15)
        if r.status_code == 200:
            fname.write_bytes(r.content)
        else:
            return None
    return str(fname)


def capture_epic():
    """Telecharge une image EPIC de la Terre (NASA)."""
    import requests
    try:
        r = requests.get("https://epic.gsfc.nasa.gov/api/natural", timeout=10).json()
        if not r:
            return None
        latest = r[-1]
        date = latest["date"].split()[0].replace("-", "/")
        url = ("https://epic.gsfc.nasa.gov/archive/natural/" + date +
               "/png/" + latest["image"] + ".png")
        img = requests.get(url, timeout=20)
        if img.status_code == 200:
            return img.content
    except Exception:
        pass
    return None


def assembler_video(session_dir, fps=10, output_name=None):
    if not has_ffmpeg():
        return None, "ffmpeg non installe (pkg install ffmpeg -y)"

    session_dir = Path(session_dir)
    frames = sorted(session_dir.glob("frame_*.png"))
    if len(frames) < 2:
        return None, "Pas assez de frames (" + str(len(frames)) + ")"

    output_name = output_name or (session_dir.name + ".mp4")
    output = session_dir / output_name

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(session_dir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            str(output),
        ], check=True, capture_output=True, timeout=120)
        return str(output), None
    except subprocess.CalledProcessError as e:
        return None, "ffmpeg error : " + (e.stderr.decode()[:200] if e.stderr else "")
    except Exception as e:
        return None, str(e)


def capture_sequence(n=20, interval=2):
    session = nouvelle_session()
    for i in range(n):
        img = capture_epic()
        if img:
            capture_frame(session, image_bytes=img)
            print("  Frame " + str(i+1) + "/" + str(n))
        if i < n - 1:
            time.sleep(interval)
    return session


def lister_sessions():
    if not TL_DIR.exists():
        return []
    return sorted([d for d in TL_DIR.iterdir() if d.is_dir()], reverse=True)


if __name__ == "__main__":
    print("Test iss_timelapse.py\n")
    print("ffmpeg :", has_ffmpeg())
    print("Sessions existantes :", len(lister_sessions()))
    if not has_ffmpeg():
        print("\nInstalle ffmpeg :")
        print("  pkg install ffmpeg -y")
