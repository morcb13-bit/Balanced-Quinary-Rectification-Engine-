import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- 設定 ---
np.random.seed(42)
dt = 1.0          # 1秒/ステップ
gps_phase = 30    # GPS有効区間（秒）
lost_phase = 30   # ロスト区間（秒）
total = gps_phase + lost_phase

# --- 真の軌跡（北方向に一定速度で歩く）---
true_speed = 1.2   # m/s（徒歩）
true_heading = np.radians(10)  # 北からわずかに東

true_x = np.cumsum(np.ones(total) * true_speed * np.sin(true_heading) * dt)
true_y = np.cumsum(np.ones(total) * true_speed * np.cos(true_heading) * dt)

# --- センサーデータ（加速度+ジャイロ、ノイズあり）---
accel_noise = 0.15   # m/s²
gyro_noise  = np.radians(2)  # rad/s

accel = true_speed + np.random.normal(0, accel_noise, total)
gyro  = np.random.normal(0, gyro_noise, total)  # 直進なので角速度≈0

# --- GPS観測値（有効区間のみ）---
gps_noise = 3.0  # m
gps_x = true_x[:gps_phase] + np.random.normal(0, gps_noise, gps_phase)
gps_y = true_y[:gps_phase] + np.random.normal(0, gps_noise, gps_phase)

# =============================================================
# Model A: 現状（ロスト中は止まる）
# =============================================================
est_a_x = np.zeros(total)
est_a_y = np.zeros(total)
for t in range(gps_phase):
    est_a_x[t] = gps_x[t]
    est_a_y[t] = gps_y[t]
# ロスト中は最後のGPS位置で止まる
for t in range(gps_phase, total):
    est_a_x[t] = est_a_x[gps_phase - 1]
    est_a_y[t] = est_a_y[gps_phase - 1]

# =============================================================
# Model B: B-QRE デッドレコニング
# 加速度を平衡5進数にマッピングして方向と速度を保持
# =============================================================
def to_balanced_quinary(value, unit=0.5):
    """連続値を{-2,-1,0,1,2}にマッピング"""
    raw = value / unit
    quantized = int(np.sign(raw) * min(2, round(abs(raw))))
    return quantized

est_b_x = np.zeros(total)
est_b_y = np.zeros(total)
heading = 0.0
speed_state = 0

for t in range(gps_phase):
    est_b_x[t] = gps_x[t]
    est_b_y[t] = gps_y[t]
    # GPS有効中に移動状態を学習
    if t > 0:
        dx = gps_x[t] - gps_x[t-1]
        dy = gps_y[t] - gps_y[t-1]
        heading = np.arctan2(dx, dy)
        speed_state = to_balanced_quinary(np.sqrt(dx**2 + dy**2), unit=0.6)

# ロスト中: 学習した状態＋センサーで推定
unit = 0.6
for t in range(gps_phase, total):
    i = t - gps_phase
    # ジャイロで方向更新
    heading += gyro[t] * dt
    # 加速度を平衡5進数に量子化
    speed_state = to_balanced_quinary(accel[t], unit=unit)
    # 移動量推定
    est_speed = speed_state * unit
    est_b_x[t] = est_b_x[t-1] + est_speed * np.sin(heading) * dt
    est_b_y[t] = est_b_y[t-1] + est_speed * np.cos(heading) * dt

# =============================================================
# 誤差計算（ロスト区間のみ）
# =============================================================
err_a = np.sqrt((est_a_x[gps_phase:] - true_x[gps_phase:])**2 +
                (est_a_y[gps_phase:] - true_y[gps_phase:])**2)
err_b = np.sqrt((est_b_x[gps_phase:] - true_x[gps_phase:])**2 +
                (est_b_y[gps_phase:] - true_y[gps_phase:])**2)

print("=== ロスト区間（30秒）の誤差 ===")
print(f"Model A（止まる）  最終誤差: {err_a[-1]:.2f} m, 平均: {err_a.mean():.2f} m")
print(f"Model B（B-QRE）   最終誤差: {err_b[-1]:.2f} m, 平均: {err_b.mean():.2f} m")
print(f"改善: {err_a[-1] - err_b[-1]:.2f} m")

# =============================================================
# プロット
# =============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# 左: 軌跡
ax = axes[0]
ax.plot(true_x, true_y, 'g-', linewidth=2.5, label='True path')
ax.plot(gps_x, gps_y, 'b.', alpha=0.5, label='GPS observations')
ax.plot(est_a_x, est_a_y, 'r--', linewidth=1.5, label='Model A: Stopped')
ax.plot(est_b_x, est_b_y, 'orange', linewidth=1.5, label='Model B: B-QRE')

# ロスト区間の開始点
ax.axvline(x=true_x[gps_phase], color='gray', linestyle=':', alpha=0.5)
ax.plot(true_x[gps_phase], true_y[gps_phase], 'k^', markersize=10, label='GPS lost')
ax.plot(true_x[-1], true_y[-1], 'k*', markersize=12, label='True end (30s later)')

ax.set_xlabel('East (m)')
ax.set_ylabel('North (m)')
ax.set_title('Trajectory: Terminal Station Dead Reckoning')
ax.legend(fontsize=8)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# 右: ロスト区間の誤差
ax2 = axes[1]
t_lost = np.arange(lost_phase)
ax2.plot(t_lost, err_a, 'r--', linewidth=2, label=f'Model A (stopped) final={err_a[-1]:.1f}m')
ax2.plot(t_lost, err_b, 'orange', linewidth=2, label=f'Model B (B-QRE) final={err_b[-1]:.1f}m')
ax2.fill_between(t_lost, err_a, err_b, alpha=0.2, color='green', label='Improvement')
ax2.set_xlabel('Seconds after GPS lost')
ax2.set_ylabel('Position error (m)')
ax2.set_title('Error during GPS lost period')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/bqre_deadreckoning.png', dpi=150, bbox_inches='tight')
print("\nプロット保存完了")
