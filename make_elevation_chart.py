# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///
"""Draw the FT104 elevation profile with waypoints and planned times.

Reads the GPX written by make_waypoint_gpx.py. Each waypoint is placed on the
track by matching its plan <time> to the track's plan timestamps, so out-and-back
points (X, Y, Z, cpA, cpB) land at the right pass.

    uv run make_elevation_chart.py FT104_waypoints.gpx ft104_elevation.png
"""
import math, re, sys
from datetime import datetime, timedelta, timezone
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

src, out = (sys.argv + ["FT104_waypoints.gpx", "ft104_elevation.png"])[1:3]
s = open(src, encoding="utf-8").read()
TZ = timezone(timedelta(hours=8))
parse = lambda t: datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(TZ)

trk = [(float(a), float(b), float(e), parse(t)) for a, b, e, t in re.findall(
    r'<trkpt lat="([^"]+)" lon="([^"]+)"><ele>([^<]+)</ele><time>([^<]+)</time>', s)]
wps = [(float(e), parse(t), n, sym) for e, t, n, sym in re.findall(
    r'<wpt [^>]*><ele>([^<]+)</ele><time>([^<]+)</time><name>([^<]+)</name>.*?<sym>([^<]+)</sym>', s)]

def hav(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    a = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742000 * math.asin(math.sqrt(a))
km = [0.0]
for i in range(1, len(trk)): km.append(km[-1] + hav(trk[i - 1], trk[i]) / 1000)
ele = [p[2] for p in trk]
gain = sum(max(b - a, 0) for a, b in zip(ele, ele[1:]))
times = [p[3] for p in trk]
def idx_at(t): return min(range(len(times)), key=lambda i: abs((times[i] - t).total_seconds()))

# ---- tokens (dataviz reference palette, light) ----
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, BLUE_FILL, NIGHT = "#2a78d6", "#d6e6f8", "#efeee9"
for f in ("Heiti TC", "PingFang TC", "Noto Sans CJK TC", "Arial Unicode MS"):
    if any(f == x.name for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = [f, "DejaVu Sans"]; break
plt.rcParams.update({"axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "font.size": 10})

fig, ax = plt.subplots(figsize=(18, 7.5), dpi=150)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
YMIN, YMAX = 300, 2350
ax.set_xlim(0, km[-1]); ax.set_ylim(YMIN, YMAX)

# night band on the plan (sunset ~18:45, sunrise ~05:20 in late July, Nantou)
def is_night(t): m = t.hour * 60 + t.minute; return m >= 18 * 60 + 45 or m < 5 * 60 + 20
start = None
for i, t in enumerate(times + [None]):
    n = t is not None and is_night(t)
    if n and start is None: start = km[i]
    if not n and start is not None:
        ax.axvspan(start, km[i - 1], color=NIGHT, zorder=0, lw=0)
        ax.text((start + km[i - 1]) / 2, YMIN + 40, "night (on plan)", ha="center", color=MUTED, fontsize=9)
        start = None

ax.grid(axis="y", color=GRID, lw=0.8, zorder=1)
ax.fill_between(km, ele, YMIN, color=BLUE_FILL, lw=0, zorder=2)
ax.plot(km, ele, color=BLUE, lw=2, zorder=3, solid_joinstyle="round")

# ---- waypoints: spread label x positions so rotated labels don't collide ----
pts = []
for e, t, name, sym in wps:
    i = idx_at(t); cp = sym in ("Food",) or name.startswith(("START", "FINISH"))
    pts.append(dict(x=km[i], y=ele[i], name=name, t=t, cp=cp, sym=sym))
GAP = 1.75
lx = [p["x"] for p in pts]
for _ in range(200):  # relax toward evenly spaced, keep order
    for k in range(1, len(lx)):
        if lx[k] - lx[k - 1] < GAP:
            mid = (lx[k] + lx[k - 1]) / 2; lx[k - 1], lx[k] = mid - GAP / 2, mid + GAP / 2
    lx = [min(max(v, 0.6), km[-1] - 0.6) for v in lx]
LABEL_Y = 2150
for p, x in zip(pts, lx):
    strong = p["cp"] or p["sym"] in ("Summit", "U-Turn", "Valley", "Trail Head")
    ax.plot([p["x"], p["x"], x], [p["y"] + 25, LABEL_Y - 140, LABEL_Y - 40], color=MUTED if strong else GRID,
            lw=0.8, zorder=2.5)
    ax.scatter([p["x"]], [p["y"]], s=46 if strong else 22, color=BLUE if strong else SURF,
               edgecolor=BLUE if not strong else SURF, linewidth=1.6, zorder=4)
    ax.text(x, LABEL_Y, f"{p['name']}  {p['t']:%H:%M}", rotation=90, ha="center", va="bottom",
            fontsize=9 if strong else 8, color=INK if strong else MUTED,
            zorder=5)

ax.set_xlabel("distance on GPX (km)"); ax.set_ylabel("elevation (m)")
for side in ("top", "right"): ax.spines[side].set_visible(False)
ax.tick_params(length=0)
ax.set_xticks(range(0, int(km[-1]) + 1, 10))
ax.set_ylim(YMIN, LABEL_Y + 820)
ax.set_yticks(range(500, 2101, 250))

fig.text(0.055, 0.965, "Formosa Trail 104K — elevation profile", fontsize=17, fontweight="bold", color=INK, va="top")
fig.text(0.055, 0.925,
         f"{km[-1]:.1f} km on GPX (official 103.5)  ·  +{gain:.0f} m / −{gain:.0f} m  ·  high point 大尖山 {max(ele):.0f} m  ·  "
         f"times = plan at cutoff pace, start {times[0]:%H:%M} → finish {times[-1]:%H:%M}  ·  "
         "bold = aid station / summit / turn / key point, grey = junction",
         fontsize=10, color=INK2, va="top")
fig.subplots_adjust(left=0.055, right=0.985, top=0.89, bottom=0.08)
fig.savefig(out, facecolor=SURF)
print("wrote", out)
