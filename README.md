# Formosa Trail 104K – GPX with waypoints

The official Formosa Trail 2025 104K GPX (`FT104.gpx`) is only a bare track: it has no checkpoints, cutoffs or turn information.
This repo creates `FT104_waypoints.gpx` from it. The new file keeps the same 8,096 track points and adds 21 waypoints built from the official distance table (`distancetable.txt`).

## Files

| File | What it is |
|---|---|
| `FT104.gpx` | Official track (GpsPrune export, GPX 1.0) |
| `distancetable.txt` | Official distance / elevation / cutoff table |
| `ft104kcoursepic.png` | Course map (schematic, not to scale) |
| `make_waypoint_gpx.py` | Script that creates the new GPX (Python 3 standard library only) |
| `FT104_waypoints.gpx` | **Output to load onto your watch or app** (GPX 1.1) |

## What each waypoint has

- **A short name** of 15 characters or fewer, with the official km, e.g. `cpA-1 13.4`, `TURN 18.1`, `cpD Bag 50.0`
- **A description** (`<cmt>` and `<desc>`) with:
  - the official km and the km along the GPX track
  - the elevation
  - the cutoff and DNF rule
  - a **direction cue** at junctions (turn left/right, compass heading, which way the other branch goes)
  - a **NEXT** line: distance and climb/descent to the next waypoint
- **An icon type** (`<sym>` / `<type>`): `Left` / `Right` at junctions, `Food` at checkpoints, `Summit`, `Valley`, `U-Turn`. Garmin turns these into course-point alerts. Garmin may show `U-Turn` as a generic point.

| Waypoint | Official km | Notes |
|---|---|---|
| START | 0.0 | 04:00 start |
| J1 Fork | (3.5) | Return route rejoins here near the end |
| X out | 10.5 | Start of the out-and-back |
| cpA-1 | 13.4 | Cutoff 08:15 |
| TURN | 18.1 | U-turn |
| cpA-2 | 22.8 | Cutoff 10:15 |
| X ret | 25.6 | Leave the out-and-back toward Y |
| Y out | 31.9 | |
| cpB-1 | 34.2 | Cutoff 14:00 |
| Z out | 40.0 | |
| W/cpC | 44.6 | 14:00(14:30) 104→75K; 16:00 DNF |
| cpD Bag | 50.0 | Drop bag, leave before 15:30 |
| TrailHead | 54.3 | Start of the +1420 m climb |
| Dajianshan | 61.5 | 大尖山 2017 m, high point |
| cpC2 | 71.8 | Cutoff 22:00 |
| Z ret | 76.6 | |
| Wujie | 86.4 | 武界, low point |
| cpB-2 | 89.6 | Cutoff 04:00 |
| Y ret | 91.9 | |
| J1 Merge | (99.3) | Back on the first 3.5 km |
| FINISH | 103.5 | Cutoff 08:00 |

## How the waypoints are placed

- **Junctions** (X, Y, cpB, Z, W/cpC2, J1): the script finds where the track runs over the same ground twice, at least 1.5 km apart along the course. The point where the two passes split is the junction. Each pass gets its own waypoint and its own left/right cue, worked out from the branch you take versus the branch you don't.
- **Turn point:** where the track doubles back on itself.
- **大尖山 / Wujie / Trail entry:** the highest point overall, and the lowest points near 86 km and 54 km.
- **cpA, cpD:** by distance. cpD is placed 4.3 km before the trail entry, as the table says.

## Caveats

- The GPX measures **102.85 km**, not 103.5 km. Later waypoints come up to about 0.8 km earlier than their official km.
- **cpD is the least certain point.** Nothing in the track marks it, so it could be off by a few hundred meters.
- **Junction positions can be about 50–100 m off** because of GPS drift where the two passes overlap. Treat the cues as a guide.
- The track timestamps come from the original export and are **fake (about 15 km/h)**. Ignore any virtual-partner pace based on them.

## Regenerate

```sh
python3 make_waypoint_gpx.py FT104.gpx FT104_waypoints.gpx
```
