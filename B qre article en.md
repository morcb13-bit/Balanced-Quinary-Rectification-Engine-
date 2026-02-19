# B-QRE: Filling the 30-Second GPS Blind Spot with Balanced Quinary

**Balanced Quinary Rectification Engine — Proof of Concept**

2026

---

## Why I Wrote This

The moment you walk through the ticket gates at a large terminal station, your navigation app freezes.

The same thing happens coming up from underground, or deep in an urban canyon. **When GPS signal is lost, most apps simply stop updating your position.** Thirty seconds later when the signal returns, the blue dot teleports to somewhere else entirely.

The problem of not knowing which direction you're facing isn't a precision issue — it's the result of **doing nothing during signal loss.**

This article proposes **B-QRE**, an algorithm that uses the symmetric properties of **Balanced Quinary notation** to keep estimating your position using onboard sensors even when GPS is unavailable.

---

## What Is Balanced Quinary?

Standard quinary uses `{0, 1, 2, 3, 4}`.  
**Balanced Quinary uses `{-2, -1, 0, 1, 2}`.**

The state set is symmetric around zero. That property is the key.

### Why This Helps with Sensor Noise

A smartphone's accelerometer always contains small random noise.  
If you integrate that noise continuously as a floating-point value, errors accumulate and your estimated position slowly drifts.

When quantized to Balanced Quinary, random noise is rounded to one of `{-2, -1, 0, 1, 2}`.  
Because the state set is zero-symmetric, **the expected value of random noise becomes exactly 0, suppressing long-term drift using only integer arithmetic.**

```python
def to_balanced_quinary(value, unit=0.5):
    """Map a continuous value to {-2, -1, 0, 1, 2}"""
    raw = value / unit
    return int(np.sign(raw) * min(2, round(abs(raw))))
```

---

## The B-QRE Algorithm

### Processing Flow

```
[GPS Active]
  Learn movement direction and speed from GPS observations
  → Store as Balanced Quinary state

[Signal Loss Detected]
  Switch to dead reckoning mode

[During Loss]
  Update heading with gyroscope
  Quantize acceleration to Balanced Quinary → estimate movement
  Continue updating position

[Signal Recovered]
  Converge to GPS-observed position
```

### Core Implementation (Python)

```python
import numpy as np

def to_balanced_quinary(value, unit=0.5):
    raw = value / unit
    return int(np.sign(raw) * min(2, round(abs(raw))))

def bqre_dead_reckoning(gps_x, gps_y, accel, gyro, gps_phase, total, dt=1.0, unit=0.6):
    est_x = np.zeros(total)
    est_y = np.zeros(total)
    heading = 0.0

    # GPS active: use observations directly, learn heading
    for t in range(gps_phase):
        est_x[t] = gps_x[t]
        est_y[t] = gps_y[t]
        if t > 0:
            dx = gps_x[t] - gps_x[t-1]
            dy = gps_y[t] - gps_y[t-1]
            heading = np.arctan2(dx, dy)

    # Lost: estimate using sensors + Balanced Quinary
    for t in range(gps_phase, total):
        heading += gyro[t] * dt                             # update heading via gyro
        speed_state = to_balanced_quinary(accel[t], unit)  # quantize acceleration
        est_speed = speed_state * unit
        est_x[t] = est_x[t-1] + est_speed * np.sin(heading) * dt
        est_y[t] = est_y[t-1] + est_speed * np.cos(heading) * dt

    return est_x, est_y
```

---

## Simulation Experiment

### Setup

| Parameter | Value |
|---|---|
| Total duration | 60 seconds (1 step = 1 second) |
| GPS active period | 0–29 seconds |
| Signal lost period | 30–59 seconds |
| True walking speed | 1.2 m/s |
| Heading | 10 degrees east of north |
| GPS observation noise | Std dev 3.0 m |
| Accelerometer noise | Std dev 0.15 m/s² |
| Gyroscope noise | Std dev 2 deg/s |
| Balanced Quinary unit `u` | 0.6 m/s |

### Models Compared

- **Model A (conventional)**: Position freezes at last known GPS fix when signal is lost
- **Model B (B-QRE)**: Balanced Quinary quantization + gyroscope-based dead reckoning

### Results

| Metric | Model A (frozen) | Model B (B-QRE) |
|---|---|---|
| Position error after 30s loss | **27.81 m** | **12.69 m** |
| Average error during loss | 12.04 m | 9.77 m |
| Final error improvement | — | **15.12 m reduction (≈54%)** |

After 30 seconds of signal loss, Model A shows a position nearly 28 m from the true location. B-QRE stays within 13 m. For the practical use case of **deciding which direction to walk after exiting a ticket gate**, this difference is meaningful.

---

## Honest Limitations

This article is a Proof of Concept. **No real-device validation has been conducted.** The following points are open questions:

- `unit = 0.6 m/s` is tuned for this simulation. Real-world optimal values will vary by device and walking speed
- In a separate experiment, B-QRE showed no advantage over simple clipping for spike noise suppression
- Scenarios with frequent sharp acceleration or direction changes may be affected by the coarseness of discrete states
- Real-device validation requires Android GNSS Raw Measurements logs

**The "54% improvement" figure will differ on real hardware. Please do not use this number as a basis for adoption decisions.**

---

## What's Next

- [ ] Validate with real Android GNSS Raw Measurements logs
- [ ] Dynamic adaptation of `unit` based on movement speed
- [ ] Hybrid implementation with EKF
- [ ] Extension to 2D and 3D
- [ ] Evaluation in environments with frequent spike noise

---

## Repository

Full code: [GitHub — URL to be added]  
License: MIT

Feedback and pull requests are welcome.

---

*© 2026. Shared as a contribution to the commons.*
