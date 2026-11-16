# Formosa Trail 104K – GPX with waypoints

The official Formosa Trail 2025 104K GPX (`FT104.gpx`) is only a bare track: it has no checkpoints, cutoffs or turn information.
Official course info (map, GPX, checkpoints, cutoffs): **[Formosa Trail – Course 賽道](https://formosatrail.com/zh/course/)**.

This repo creates `FT104_waypoints.gpx` from it. The new file keeps the same 8,096 track points, adds 21 waypoints built from the official distance table (`distancetable.txt`), and replaces the fake timestamps with a **cutoff-based pace plan**.

![FT104 elevation profile, 24 h plan](ft104_elevation_24h.png)

Cutoff-pace (28 h) version: [`ft104_elevation.png`](ft104_elevation.png)

## Files

| File | What it is |
|---|---|
| `FT104.gpx` | Official track from the [course page](https://formosatrail.com/zh/course/) (GpsPrune export, GPX 1.0) |
| `distancetable.txt` | Official distance / elevation / cutoff table, from the [course page](https://formosatrail.com/zh/course/) |
| `ft104kcoursepic.png` | Course map (schematic, not to scale) |
| `make_waypoint_gpx.py` | Script that creates the new GPX (Python 3 standard library only) |
| `FT104_waypoints.gpx` | **Output to load onto your watch or app** (GPX 1.1), plan = cutoff pace (28 h) |
| `FT104_24h.gpx` | Same, plan = 24 h finish (`--finish-hours 24`) |
| `make_elevation_chart.py` | Draws the elevation chart from the output GPX (`uv run`, pulls in matplotlib) |
| `ft104_elevation.png` / `ft104_elevation_24h.png` | Elevation profile for the 28 h / 24 h plan: checkpoints highlighted, planned times, night hours, water/food gaps |

## Checkpoints – the only water/food

| Checkpoint | Name | Official km | Cutoff |
|---|---|---|---|
| cpA-1 / cpA-2 | Tea Farm 茶園 | 13.4 / 22.8 | 08:15 / 10:15 |
| cpB-1 / cpB-2 | Orange House Wujie 武界橘子屋 | 34.2 / 89.6 | 14:00 / 04:00 |
| cpD | Zhong Zheng 中正 (church), **drop bag** | 50.0 | leave before 15:30 |
| cpC2 | House, 卓社林道 (Zhuoshe forest road 5K) | 71.8 | 22:00 |

The 104K doesn't detour into cpC1 at W (44.6 km), so W has **no** water/food. The longest stretch without supplies is **cpD → cpC2: 21.4 km, +1574 m**, over 大尖山. That's about 6 h on the 24 h plan and 7 h at cutoff pace.

## What each waypoint has

- **A short name** with the official km, plus the Chinese name for checkpoints, e.g. `cpA-1 茶園 13.4`, `TURN 18.1`, `cpD Bag 中正 50.0`
- **A description** (`<cmt>` and `<desc>`) with:
  - the official km and the km along the GPX track
  - the elevation
  - the planned arrival time, plus the cutoff and buffer at checkpoints, e.g. `PLAN 07:37 (cutoff 08:15, buffer 37 min)`
  - the cutoff and DNF rule
  - a **direction cue** at junctions (turn left/right, compass heading, which way the other branch goes)
  - `WATER/FOOD available` at checkpoints, and on every waypoint a **NEXT WATER/FOOD** line: the next checkpoint, distance, climb and planned time
  - a **NEXT** line: distance and climb/descent to the next waypoint
- **An icon type** (`<sym>` / `<type>`): `Left` / `Right` at junctions, `Food` at checkpoints, `Summit`, `Valley`, `U-Turn`. Garmin turns these into course-point alerts. Garmin may show `U-Turn` as a generic point.

| Waypoint | Official km | Plan 28 h | Plan 24 h | Notes |
|---|---|---|---|---|
| START | 0.0 | 04:00 | 04:00 | 04:00 start |
| J1 Fork | (3.5) | 04:37 | 04:31 | Return route rejoins here near the end |
| X out | 10.5 | 07:06 | 06:40 | Start of the out-and-back |
| **cpA-1 茶園** | 13.4 | 07:37 | 07:06 | Cutoff 08:15 |
| TURN | 18.1 | 08:34 | 07:55 | U-turn |
| **cpA-2 茶園** | 22.8 | 09:28 | 08:41 | Cutoff 10:15 |
| X ret | 25.6 | 10:09 | 09:16 | Leave the out-and-back toward Y |
| Y out | 31.9 | 11:33 | 10:28 | |
| **cpB-1 橘子屋** | 34.2 | 11:56 | 10:48 | Cutoff 14:00 |
| Z out | 40.0 | 13:09 | 11:50 | |
| W/cpC | 44.6 | **14:00** | 12:34 | 14:00(14:30) 104→75K; 16:00 DNF. No water/food |
| **cpD Bag 中正** | 50.0 | 15:01 | 13:26 | Drop bag, leave before 15:30 |
| TrailHead | 54.3 | 15:51 | 14:10 | Start of the +1420 m climb |
| Dajianshan | 61.5 | 19:52 | 17:36 | 大尖山 2017 m, high point |
| **cpC2 卓社** | 71.8 | **22:00** | 19:25 | Cutoff 22:00 |
| Z ret | 76.6 | 23:35 | 20:47 | |
| Wujie | 86.4 | 01:56 | 22:48 | 武界, low point |
| **cpB-2 橘子屋** | 89.6 | 03:53 | 00:28 | Cutoff 04:00 |
| Y ret | 91.9 | 05:09 | 01:33 | |
| J1 Merge | (99.3) | 07:09 | 03:16 | Back on the first 3.5 km |
| FINISH | 103.5 | **08:00** | 04:00 | Cutoff 08:00 |

## Pace plan (track timestamps)

Every track point is timestamped, so a watch's **virtual partner** follows the plan.

- **Effort model:** time is spread by ITRA km-effort (`km + D+/100`), so climbs get more time per km than flats and descents.
- **Fitted to the cutoffs:** the plan is the latest schedule that never misses a 104K cutoff, with a pace that only ever slows down (realistic for a 28 h race). Technically, it is the greatest convex minorant of the (effort, cutoff) points.
- **Binding cutoffs:** at the default 28 h, these are W 14:00 (stay on the 104K), cpC2 22:00 and the finish 08:00. The other checkpoints come out with buffer.
- **Default 28 h = cutoff pace.** Falling behind the virtual partner means you are on track to miss a cutoff. To plan with a margin, scale the whole plan to your target time with `--finish-hours`, e.g. `--finish-hours 24` reaches W at 12:34 and the finish at 04:00.
- **Start time:** 04:00 local (UTC+8). The default date is the track's original date (2025-07-24). Set the real race date with `--start YYYY-MM-DDT04:00`.

## How the waypoints are placed

- **Junctions** (X, Y, cpB, Z, W/cpC2, J1): the script finds where the track runs over the same ground twice, at least 1.5 km apart along the course. The point where the two passes split is the junction. Each pass gets its own waypoint and its own left/right cue, worked out from the branch you take versus the branch you don't.
- **Turn point:** where the track doubles back on itself.
- **大尖山 / Wujie / Trail entry:** the highest point overall, and the lowest points near 86 km and 54 km.
- **cpA, cpD:** by distance. cpD is placed 4.3 km before the trail entry, as the table says.

## Caveats

- This repo is unofficial. If anything here disagrees with the [official course page](https://formosatrail.com/zh/course/) or race briefing, the official information wins.
- The GPX measures **102.85 km**, not 103.5 km. Later waypoints come up to about 0.8 km earlier than their official km.
- **cpD is the least certain point.** Nothing in the track marks it, so it could be off by a few hundred meters.
- **Junction positions can be about 50–100 m off** because of GPS drift where the two passes overlap. Treat the cues as a guide.
- The pace plan doesn't account for terrain difficulty, night running or time spent at aid stations. Treat it as a schedule check, not a prediction.
- The table lists cpB-1 and W both at 14:00, which can't both be met. The plan treats W 14:00 as the binding one, so cpB-1 is planned for about 11:56.

## Regenerate

```sh
python3 make_waypoint_gpx.py FT104.gpx FT104_waypoints.gpx
# with options:
python3 make_waypoint_gpx.py FT104.gpx FT104_24h.gpx --finish-hours 24   # add --start YYYY-MM-DDT04:00 for the race date
# elevation charts (labels show the plan times inside the GPX you pass in):
uv run make_elevation_chart.py FT104_waypoints.gpx ft104_elevation.png
uv run make_elevation_chart.py FT104_24h.gpx ft104_elevation_24h.png
```
