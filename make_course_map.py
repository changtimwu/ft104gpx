# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///
"""Draw a simple FT104 course map with direction arrows from the waypoint GPX.

Each direction of travel is drawn slightly to its right (like lanes on a road), so
out-and-back and shared sections show two parallel lines with opposite arrows.

    uv run make_course_map.py FT104_waypoints.gpx ft104_course_map.png
"""
import math, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

src, out = (sys.argv + ["FT104_waypoints.gpx", "ft104_course_map.png"])[1:3]
s = open(src, encoding="utf-8").read()
trk = [(float(a), float(b), float(e)) for a, b, e in re.findall(
    r'<trkpt lat="([^"]+)" lon="([^"]+)"><ele>([^<]+)</ele>', s)]
from datetime import datetime, timedelta, timezone
TZ = timezone(timedelta(hours=8))
hhmm = lambda t: datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(TZ).strftime("%H:%M")
wps = [(float(a), float(b), n, sym, hhmm(t)) for a, b, t, n, sym in re.findall(
    r'<wpt lat="([^"]+)" lon="([^"]+)"><ele>[^<]+</ele><time>([^<]+)</time><name>([^<]+)</name>.*?<sym>([^<]+)</sym>', s)]
hours = float((re.search(r"pace plan, ([\d.]+) h finish", s) or [0, 28])[1])
PLAN = "cutoff pace (28 h)" if abs(hours - 28) < 1e-6 else f"{hours:g} h finish"

# ---- local projection in km ----
LAT0 = sum(p[0] for p in trk) / len(trk); LON0 = sum(p[1] for p in trk) / len(trk)
KX, KY = 111.32 * math.cos(math.radians(LAT0)), 110.57
xy = lambda lat, lon: ((lon - LON0) * KX, (lat - LAT0) * KY)
P = [xy(p[0], p[1]) for p in trk]
D = [0.0]
for a, b in zip(P, P[1:]): D.append(D[-1] + math.dist(a, b))
import bisect
def at(d): return max(0, min(bisect.bisect_left(D, d), len(D) - 1))

# ---- shift every point to the right of travel (smoothed heading over ±120 m) ----
OFF = 0.075
Q = []
for i, (x, y) in enumerate(P):
    a, b = P[at(D[i] - 0.12)], P[at(D[i] + 0.12)]
    hx, hy = b[0] - a[0], b[1] - a[1]; n = math.hypot(hx, hy) or 1
    Q.append((x + hy / n * OFF, y - hx / n * OFF))

# ---- tokens (dataviz reference palette, light) ----
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
ROUTE, BLUE_DARK, CP_FILL = "#2a78d6", "#1c5aa6", "#1c5aa6"
for f in ("Heiti TC", "PingFang TC", "Noto Sans CJK TC", "Arial Unicode MS"):
    if any(f == x.name for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = [f, "DejaVu Sans"]; break

xs, ys = [q[0] for q in Q], [q[1] for q in Q]
pad = 1.6
W, H = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
fig = plt.figure(figsize=(12, 12 * H / W + 1.4), dpi=150)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96 * (12 * H / W) / (12 * H / W + 1.4)])
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.set_xlim(min(xs) - pad, max(xs) + pad); ax.set_ylim(min(ys) - pad, max(ys) + pad)
ax.set_aspect("equal"); ax.axis("off")

# 1 km grid, very faint
for gx in range(math.floor(min(xs) - pad), math.ceil(max(xs) + pad) + 1):
    ax.axvline(gx, color=GRID, lw=0.5, zorder=0)
for gy in range(math.floor(min(ys) - pad), math.ceil(max(ys) + pad) + 1):
    ax.axhline(gy, color=GRID, lw=0.5, zorder=0)

# route: white casing + line
ax.plot(xs, ys, color=SURF, lw=5.5, solid_capstyle="round", solid_joinstyle="round", zorder=2)
ax.plot(xs, ys, color=ROUTE, lw=2.2, solid_capstyle="round", solid_joinstyle="round", zorder=3)

# direction arrows every 1.2 km
STEP = 1.0
d = 0.6
while d < D[-1] - 0.3:
    i, j = at(d - 0.08), at(d + 0.08)
    ax.annotate("", xy=Q[j], xytext=Q[i], zorder=4,
                arrowprops=dict(arrowstyle="-|>,head_length=0.62,head_width=0.32", color=BLUE_DARK, lw=0,
                                shrinkA=0, shrinkB=0))
    d += STEP

# km markers every 10 km, pushed further to the right side of travel
for k in range(10, int(D[-1]) + 1, 10):
    i = at(k); a, b = P[at(k - 0.12)], P[at(k + 0.12)]
    hx, hy = b[0] - a[0], b[1] - a[1]; n = math.hypot(hx, hy) or 1
    tx, ty = P[i][0] + hy / n * 0.42, P[i][1] - hx / n * 0.42
    ax.plot([Q[i][0], tx], [Q[i][1], ty], color=MUTED, lw=0.7, zorder=3.5)
    ax.text(tx, ty, f"{k}", fontsize=8.5, color=INK2, ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.18", fc=SURF, ec=MUTED, lw=0.7))

# ---- waypoints merged by place (same spot visited twice -> one label) ----
def kmlabel(n): m = re.search(r"(\d+\.\d)$", n); return m.group(1) if m else None
places = []
for lat, lon, name, sym, tm in wps:
    p = xy(lat, lon)
    for pl in places:
        if math.dist(pl["p"], p) < 0.35 and (pl["cp"] == (sym == "Food")): pl["items"].append((name, sym, tm)); break
    else:
        places.append(dict(p=p, items=[(name, sym, tm)], cp=sym == "Food"))

def title(pl):
    names = [it[0] for it in pl["items"]]
    kms = [k for k in map(kmlabel, names) if k]
    base = re.sub(r"\s*\d+\.\d$", "", names[0])
    base = re.sub(r"-\d(?=\s|$)|\s(out|ret)$", "", base.replace("cpD Bag", "cpD"))
    return base, " / ".join(kms), " / ".join(it[2] for it in pl["items"])

# label positions (dx, dy in km from the point), tuned for this course
POS = {"START": (-1.1, 0.55), "J1": (1.0, -0.55), "X": (0.1, 0.95), "cpA": (0.0, 0.85), "TURN": (0.9, 0.6),
       "Y": (1.6, -0.35), "cpB": (-1.6, 0.0), "Z": (-1.0, 1.25), "W/cpC": (1.1, -1.5), "cpC2": (-1.65, -0.55),
       "cpD": (0.3, 1.0), "TrailHead": (-1.1, -0.9), "Dajianshan": (-1.3, 0.5), "Wujie": (1.1, -0.4),
       "FINISH": (-1.1, 0.55)}
for pl in places:
    base, kms, tms = title(pl)
    key = next((k for k in POS if base.startswith(k)), None)
    if base.startswith(("START", "FINISH")):
        continue
    dx, dy = POS.get(key, (0.9, 0.4))
    x, y = pl["p"]; tx, ty = x + dx, y + dy
    ax.plot([x, tx], [y, ty], color=MUTED, lw=0.7, zorder=3.5)
    if pl["cp"]:
        ax.scatter([x], [y], s=170, color=CP_FILL, edgecolor=SURF, linewidth=2.2, zorder=7)
        ax.text(tx, ty, f"{base}\n{kms} km\n{tms}", fontsize=10.5, color="white", ha="center", va="center", zorder=8,
                linespacing=1.25, bbox=dict(boxstyle="round,pad=0.4", fc=CP_FILL, ec="none"))
    else:
        sym = pl["items"][0][1]
        strong = sym in ("Summit", "U-Turn", "Valley", "Trail Head")
        ax.scatter([x], [y], s=55 if strong else 34, color=SURF, edgecolor=INK if strong else INK2, linewidth=1.6, zorder=7)
        nice = {"Dajianshan": "大尖山 2017 m", "TURN": "Turn point ↶", "TrailHead": "Trail entry",
                "Wujie": "Wujie 武界", "W/cpC": "W junction\nno water"}.get(base, base.replace(" Fork", "").replace(" Merge", ""))
        ax.text(tx, ty, f"{nice}\n{kms} km\n{tms}" if kms else f"{nice}\n{tms}", fontsize=9.5 if strong else 9,
                color=INK if strong else INK2, ha="center", va="center", zorder=8, linespacing=1.2,
                bbox=dict(boxstyle="round,pad=0.3", fc=SURF, ec=GRID, lw=0.8))

# start / finish flag
sx, sy = P[0]
ax.scatter([sx], [sy], s=230, marker="s", color=INK, edgecolor=SURF, linewidth=2.2, zorder=9)
ax.text(sx + POS["START"][0], sy + POS["START"][1], f"START / FINISH\n0 / 103.5 km\n{wps[0][4]} → {wps[-1][4]}", fontsize=10.5,
        color="white", ha="center", va="center", zorder=9, linespacing=1.25,
        bbox=dict(boxstyle="round,pad=0.4", fc=INK, ec="none"))
ax.plot([sx, sx + POS["START"][0]], [sy, sy + POS["START"][1]], color=MUTED, lw=0.7, zorder=3.5)

# north arrow + scale bar (bottom-left)
x0, y0 = min(xs) - pad + 0.5, min(ys) - pad + 0.6
ax.annotate("", xy=(x0 + 0.25, y0 + 1.6), xytext=(x0 + 0.25, y0 + 0.75),
            arrowprops=dict(arrowstyle="-|>,head_length=0.8,head_width=0.4", color=INK, lw=1.4))
ax.text(x0 + 0.25, y0 + 1.85, "N", ha="center", va="center", fontsize=12, color=INK)
ax.plot([x0, x0 + 2], [y0 + 0.3, y0 + 0.3], color=INK, lw=2.5, solid_capstyle="butt")
ax.plot([x0 + 1, x0 + 1], [y0 + 0.22, y0 + 0.38], color=INK, lw=1)
ax.text(x0 + 1, y0 + 0.02, "2 km   (grid = 1 km)", ha="center", va="center", fontsize=8.5, color=INK2)

top = 0.98
fig.text(0.03, top, f"Formosa Trail 104K — course map · plan: {PLAN}", fontsize=19, fontweight="bold", color=INK, va="top")
fig.text(0.03, top - 0.03,
         "Follow the arrows. Each direction is drawn on its own right-hand side, so out-and-back and shared\n"
         "sections show two lines with opposite arrows.  Blue tags = checkpoints, the only water/food.  "
         "Small boxes = km.\nTimes = planned arrival on this plan (start 04:00).", fontsize=10, color=INK2, va="top", linespacing=1.35)
fig.text(0.97, 0.012, "Route from the official GPX · formosatrail.com/zh/course · unofficial map",
         fontsize=8, color=MUTED, ha="right")
fig.savefig(out, facecolor=SURF)
print("wrote", out)
