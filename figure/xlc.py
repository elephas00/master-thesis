import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Songti SC', 'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(12, 10), dpi=150)
x = np.linspace(0, 10, 2000)

def gauss(x, mu, sigma=0.2):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

# SLC
ax1 = plt.subplot(3, 1, 1)
plt.plot(x, gauss(x, 2.5), color='#0055cc', linewidth=3.5)
plt.plot(x, gauss(x, 7.5), color='#0055cc', linewidth=3.5)
plt.title('SLC (1bit/cell)  2个电压状态', fontsize=14, pad=12)
plt.ylabel('概率', fontsize=13)
plt.xlim(0, 10)
plt.ylim(0, 1.2)
plt.grid(False)
plt.tick_params(axis='both', which='both', length=0)
plt.xticks([])
plt.yticks([])

# MLC
ax2 = plt.subplot(3, 1, 2)
for mu in [1.5, 3.5, 6.5, 8.5]:
    plt.plot(x, gauss(x, mu), color='#0055cc', linewidth=3.5)
plt.title('MLC (2bit/cell)  4个电压状态', fontsize=14, pad=12)
plt.ylabel('概率', fontsize=13)
plt.xlim(0, 10)
plt.ylim(0, 1.2)
plt.grid(False)
plt.tick_params(axis='both', which='both', length=0)
plt.xticks([])
plt.yticks([])

# TLC
ax3 = plt.subplot(3, 1, 3)
for mu in np.linspace(1, 9, 8):
    plt.plot(x, gauss(x, mu, sigma=0.17), color='#0055cc', linewidth=3.5)
plt.title('TLC (3bit/cell)  8个电压状态', fontsize=14, pad=12)
plt.xlabel('电压', fontsize=13)
plt.ylabel('概率', fontsize=13)
plt.xlim(0, 10)
plt.ylim(0, 1.2)
plt.grid(False)
plt.tick_params(axis='both', which='both', length=0)
plt.xticks([])
plt.yticks([])

plt.tight_layout()
plt.savefig('SLC_MLC_TLC_HIGH_RES.png', bbox_inches='tight', dpi=600)
plt.show()
print("✅ 超高清图片已生成（600 DPI）")