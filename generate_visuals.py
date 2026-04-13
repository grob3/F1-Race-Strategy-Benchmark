import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create seaborn style for professional look
sns.set_theme(style="whitegrid")
# Use a custom dark/light background
plt.rcParams['axes.facecolor'] = '#f8f9fa'

# ── Global Race Constants ──
TOTAL_LAPS    = 57
STARTING_FUEL = 110.0
FUEL_BURN     = 1.85
FUEL_EFFECT   = 0.035
PIT_STOP_LOSS = 22.0

# Using custom colors for the tires: Soft=Red, Medium=Yellow, Hard=White/DarkGray
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
    total = 0.0
    for i in range(num_laps):
        total += compute_lap_time(compound, i, start_race_lap + i)
    return total


def plot_tire_degradation():
    plt.figure(figsize=(10, 6))
    laps = np.arange(0, TOTAL_LAPS)
    
    for compound in ["Soft", "Medium", "Hard"]:
        times = [compute_lap_time(compound, lap, lap) for lap in laps]
        plt.plot(laps, times, label=f"{compound} Tire", color=COMPOUNDS[compound]['color'], linewidth=3)
        
    plt.title("Subtask 1: Tire Degradation Over 57 Laps (No Pit Stops)", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Race Lap Number", fontsize=12)
    plt.ylabel("Lap Time (Seconds)", fontsize=12)
    plt.legend(title="Tire Compound", fontsize=11, title_fontsize=12)
    plt.tight_layout()
    plt.savefig('subtask1_degradation.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_one_stop_optimization():
    plt.figure(figsize=(10, 6))
    pit_laps = np.arange(10, 47)
    race_times = []
    
    for pit_lap in pit_laps:
        s1 = _compute_stint_time('Soft', 0, pit_lap)
        s2 = _compute_stint_time('Hard', pit_lap, TOTAL_LAPS - pit_lap)
        race_times.append(s1 + PIT_STOP_LOSS + s2)
        
    optimal_idx = np.argmin(race_times)
    optimal_pit_lap = pit_laps[optimal_idx]
    optimal_time = race_times[optimal_idx]
    
    plt.plot(pit_laps, race_times, color='#2A9D8F', linewidth=3, label='Strategy Time')
    plt.scatter([optimal_pit_lap], [optimal_time], color='#E76F51', s=150, zorder=5, 
                label=f'Optimal Pit: Lap {optimal_pit_lap}\n({optimal_time:.1f}s)', marker='*')
    
    plt.title("Subtask 2: One-Stop Optimization Window (Soft → Hard)", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Pit Lap Decision", fontsize=12)
    plt.ylabel("Total Race Time (Seconds)", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('subtask2_one_stop.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_crossover_sensitivity():
    plt.figure(figsize=(10, 6))
    deg_rates = np.arange(0.010, 0.151, 0.005)
    one_stop_times = []
    two_stop_times = []
    
    original_deg = COMPOUNDS['Soft']['deg_rate']
    crossover_x, crossover_y = None, None
    found_crossover = False
    
    for deg_rate in deg_rates:
        COMPOUNDS['Soft']['deg_rate'] = deg_rate
        
        # Best One Stop
        best_one = float('inf')
        for p in range(10, 47):
            t = _compute_stint_time('Soft', 0, p) + PIT_STOP_LOSS + _compute_stint_time('Hard', p, TOTAL_LAPS - p)
            if t < best_one:
                best_one = t
                
        # Best Two Stop (Optimized grid search for plot speed)
        best_two = float('inf')
        # We sample every element carefully
        for p1 in range(10, 37, 2):
            for p2 in range(p1 + 10, 47, 2):
                t = (_compute_stint_time('Soft', 0, p1) + PIT_STOP_LOSS + 
                     _compute_stint_time('Medium', p1, p2-p1) + PIT_STOP_LOSS + 
                     _compute_stint_time('Hard', p2, TOTAL_LAPS-p2))
                if t < best_two:
                    best_two = t
                    
        one_stop_times.append(best_one)
        two_stop_times.append(best_two)
        
        if not found_crossover and best_two < best_one:
            crossover_x = deg_rate
            crossover_y = best_two
            found_crossover = True

    # Restore
    COMPOUNDS['Soft']['deg_rate'] = original_deg
    
    plt.plot(deg_rates, one_stop_times, label='Optimal One-Stop (S→H)', linewidth=3, color='#F4A261')
    plt.plot(deg_rates, two_stop_times, label='Optimal Two-Stop (S→M→H)', linewidth=3, color='#264653')
    
    if crossover_x is not None:
        plt.axvline(x=crossover_x, color='gray', linestyle='--', alpha=0.7)
        plt.scatter([crossover_x], [crossover_y], color='red', s=100, zorder=5, 
                    label=f'Crossover (~{crossover_x:.3f})')
    
    plt.title("Subtask 3: Sensitivity Analysis of Soft Tire Degradation", fontsize=16, weight='bold', pad=15)
    plt.xlabel("Soft Tire Degradation Rate (sec/lap²)", fontsize=12)
    plt.ylabel("Total Race Time (Seconds)", fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig('subtask3_crossover.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating Visualization 1: Tire Degradation...")
    plot_tire_degradation()
    
    print("Generating Visualization 2: One-Stop...")
    plot_one_stop_optimization()
    
    print("Generating Visualization 3: Crossover...")
    plot_crossover_sensitivity()
    
    print("Done! Visualizations saved.")
