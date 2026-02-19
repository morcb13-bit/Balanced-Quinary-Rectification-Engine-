# B-QRE: Balanced Quinary Rectification Engine

GNSS Dead Reckoning Correction using Balanced Quinary — Proof of Concept

---

## Overview

When GPS signal is lost, your phone's position freezes.  
B-QRE fills that gap using the phone's built-in sensors and the symmetric properties of Balanced Quinary notation.

A simulation experiment showed a reduction in position error after 30 seconds of GPS loss from **27.81 m → 12.69 m (approx. 54% improvement)**.

**This repository is a Proof of Concept. Real-device validation has not yet been conducted.**

---

## File Structure

```
├── README.md           # This file
├── bqre_simulation.py  # Simulation code
└── B-QRE_article.md    # Technical article (detailed explanation)
```

---

## How to Run

```bash
pip install numpy matplotlib
python bqre_simulation.py
```

Output: Simulation result graph (PNG) and RMSE values

---

## License

MIT License

Feedback and pull requests are welcome.
