"""Stage C: frame extraction into timestamped contact sheets.

Usage:
  survey:  python3 frame_sheets.py survey video.mp4 out_prefix \
              [offset=0] [every_s=7] [tile_w=270]
  burst:   python3 frame_sheets.py burst  video.mp4 out_prefix \
              start_s dur_s fps [offset=0] [tile_w=240]

`offset` is added to every burned-in timestamp so multi-part videos
report one global timeline.  Survey first (baseline, one-take check,
posture vocabulary, on-screen text), then bursts at the moments Stages
A and B flagged.  Blindness rule: do not run this until the Stage A
write-up and Stage B comparison are committed in the conversation.
"""
import sys, subprocess, glob, os, math, tempfile
from PIL import Image, ImageDraw, ImageFont

try:
    FONT = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except Exception:
    FONT = ImageFont.load_default()

def mmss(t):
    return f"{int(t//60)}:{t%60:04.1f}"

def extract(src, start, dur, fps, width, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t",
                    str(dur), "-i", src, "-vf",
                    f"fps={fps},scale={width}:-2",
                    f"{tmp}/f_%04d.png"], check=True)
    return sorted(glob.glob(f"{tmp}/f_*.png"))

def sheet(files, labels, cols, outpath):
    ims = [Image.open(f) for f in files]
    w, h = ims[0].size
    rows = math.ceil(len(ims)/cols)
    S = Image.new("RGB", (cols*w, rows*h), "black")
    d = ImageDraw.Draw(S)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols)*w, (i // cols)*h
        S.paste(im, (x, y))
        try:
            wlab = int(d.textlength(lab, font=FONT)) + 10
        except AttributeError:
            wlab = 8 + 12 * len(lab)
        d.rectangle([x, y, x+wlab, y+26], fill="black")
        d.text((x+4, y+3), lab, fill="yellow", font=FONT)
    S.save(outpath)
    print("wrote", outpath)

def main():
    mode, src, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    with tempfile.TemporaryDirectory() as tmp:
        if mode == "survey":
            off = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
            every = float(sys.argv[5]) if len(sys.argv) > 5 else 7.0
            tw = int(sys.argv[6]) if len(sys.argv) > 6 else 270
            dur = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration", "-of", "csv=p=0", src],
                capture_output=True, text=True).stdout.strip())
            files = extract(src, 0, dur, 1.0/every, tw, tmp)
            labels = [mmss(off + i*every) for i in range(len(files))]
            per = 16
            for si in range(math.ceil(len(files)/per)):
                sheet(files[si*per:(si+1)*per], labels[si*per:(si+1)*per],
                      4, f"{prefix}_survey_{si}.png")
        elif mode == "burst":
            start, dur, fps = (float(sys.argv[4]), float(sys.argv[5]),
                               float(sys.argv[6]))
            off = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
            tw = int(sys.argv[8]) if len(sys.argv) > 8 else 240
            files = extract(src, start, dur, fps, tw, tmp)
            labels = [mmss(off + start + i/fps) for i in range(len(files))]
            sheet(files, labels, 6, f"{prefix}_burst_{mmss(off+start)}.png"
                  .replace(":", "m"))
        else:
            raise SystemExit("mode must be survey or burst")

if __name__ == "__main__":
    main()
