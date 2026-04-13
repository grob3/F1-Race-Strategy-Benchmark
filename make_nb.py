import nbformat as nbf

nb = nbf.v4.new_notebook()

md_intro = """# F1 Race Strategy Benchmarks: Visualizations
This notebook generates visualizations corresponding to the 3 Subtasks in the benchmark. This illustrates the physical/math reality of the environment that the Gemini agent is optimizing."""

code_imports = """!pip install matplotlib seaborn numpy --quiet
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['axes.facecolor'] = '#f8f9fa'

# Constants
TOTAL_LAPS    = 57
STARTING_FUEL = 110.0
FUEL_BURN     = 1.85
FUEL_EFFECT   = 0.035
PIT_STOP_LOSS = 22.0

COMPOUNDS = {
    'Soft':   {'base_time': 90.5, 'deg_rate': 0.080, 'color': '#E63946'},
    'Medium': {'base_time': 91.2, 'deg_rate': 0.045, 'color': '#E9C46A'},
    'Hard':   {'base_time': 92.0, 'deg_rate': 0.022, 'color': '#264653'},
}

def compute_lap_time(compound: str, lap_on_tire: int, race_lap: int) -> float:
    params = COMPOUNDS[compound]
    fuel_remaining = STARTING_FUEL - FUEL_BURN * race_lap
    return params['base_time'] + params['deg_rate'] * (lap_on_tire ** 2) + FUEL_EFFECT * fuel_remaining

def _compute_stint_time(compound: str, start_race_lap: int, num_laps: int) -> float:
    return sum(compute_lap_time(compound, i, start_race_lap + i) for i in range(num_laps))"""

md_s1 = "## Subtask 1: Tire Degradation\nShows the performance of a tire over 57 laps with no pit stops."

code_s1 = """plt.figure(figsize=(10, 6))
laps = np.arange(0, TOTAL_LAPS)
for compound in ["Soft", "Medium", "Hard"]:
    times = [compute_lap_time(compound, lap, lap) for lap in laps]
    plt.plot(laps, times, label=f"{compound} Tire", color=COMPOUNDS[compound]['color'], linewidth=3)
    
plt.title("Subtask 1: Tire Degradation Over 57 Laps", fontsize=16, weight='bold')
plt.xlabel("Race Lap Number", fontsize=12)
plt.ylabel("Lap Time (Seconds)", fontsize=12)
plt.legend()
plt.show()"""

md_s2 = "## Subtask 2: One-Stop Optimization Window\nDemonstrates the U-Curve optimization for picking a pit lap on a Soft -> Hard strategy."

code_s2 = """plt.figure(figsize=(10, 6))
pit_laps = np.arange(10, 47)
race_times = []
for pit_lap in pit_laps:
    s1 = _compute_stint_time('Soft', 0, pit_lap)
    s2 = _compute_stint_time('Hard', pit_lap, TOTAL_LAPS - pit_lap)
    race_times.append(s1 + PIT_STOP_LOSS + s2)
    
optimal_idx = np.argmin(race_times)
plt.plot(pit_laps, race_times, color='#2A9D8F', linewidth=3)
plt.scatter([pit_laps[optimal_idx]], [race_times[optimal_idx]], color='#E76F51', s=150, zorder=5, marker='*')
plt.title("Subtask 2: Total Race Time vs Pit Lap (Soft -> Hard)", fontsize=16, weight='bold')
plt.xlabel("Pit Lap Decision", fontsize=12)
plt.ylabel("Total Race Time (Seconds)", fontsize=12)
plt.show()"""

md_s3 = "## Subtask 3: Sensitivity Analysis\nDemonstrates the crossover point where Two-Stop becomes faster than One-Stop as degradation increases."

code_s3 = """plt.figure(figsize=(10, 6))
deg_rates = np.arange(0.010, 0.151, 0.005)
one_stop_times = []
two_stop_times = []
original_deg = COMPOUNDS['Soft']['deg_rate']
crossover_x = None

for deg_rate in deg_rates:
    COMPOUNDS['Soft']['deg_rate'] = deg_rate
    best_one = float('inf')
    for p in range(10, 47):
        t = _compute_stint_time('Soft', 0, p) + PIT_STOP_LOSS + _compute_stint_time('Hard', p, TOTAL_LAPS - p)
        best_one = min(best_one, t)
            
    best_two = float('inf')
    for p1 in range(10, 37, 2):
        for p2 in range(p1 + 10, 47, 2):
            t = (_compute_stint_time('Soft', 0, p1) + PIT_STOP_LOSS + 
                 _compute_stint_time('Medium', p1, p2-p1) + PIT_STOP_LOSS + 
                 _compute_stint_time('Hard', p2, TOTAL_LAPS-p2))
            best_two = min(best_two, t)
                
    one_stop_times.append(best_one)
    two_stop_times.append(best_two)
    if crossover_x is None and best_two < best_one:
        crossover_x = deg_rate

COMPOUNDS['Soft']['deg_rate'] = original_deg
plt.plot(deg_rates, one_stop_times, label='Optimal One-Stop', color='#F4A261', linewidth=3)
plt.plot(deg_rates, two_stop_times, label='Optimal Two-Stop', color='#264653', linewidth=3)
if crossover_x is not None:
    plt.axvline(x=crossover_x, color='gray', linestyle='--')
plt.title("Subtask 3: Sensitivity Analysis of Soft Tire Degradation", fontsize=16, weight='bold')
plt.xlabel("Soft Degradation Rate", fontsize=12)
plt.ylabel("Total Race Time (Seconds)", fontsize=12)
plt.legend()
plt.show()"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(md_intro),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_markdown_cell(md_s1),
    nbf.v4.new_code_cell(code_s1),
    nbf.v4.new_markdown_cell(md_s2),
    nbf.v4.new_code_cell(code_s2),
    nbf.v4.new_markdown_cell(md_s3),
    nbf.v4.new_code_cell(code_s3)
]

nbf.write(nb, 'f1_benchmark_visualizations.ipynb')
print("f1_benchmark_visualizations.ipynb created successfully")
