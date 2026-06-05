"""
Demo A: Tumbling Windows (time-based aggregation)
Shows how to group events into 60-second windows using integer division
"""
from collections import defaultdict
import time

def assign_window(event_time: float, window_size: int = 60) -> int:
    """Calculate window key for a given timestamp"""
    return int(event_time // window_size) * window_size

def demo_tumbling_window():
    print("\n" + "="*60)
    print("DEMO A: Tumbling Windows (minute-based aggregation)")
    print("="*60)
    
    # Simulated events
    base = int(time.time()) - (int(time.time()) % 60)
    events = [
        {"sensor": "A", "event_time": base + 5,   "temperature": 22.0},
        {"sensor": "A", "event_time": base + 25,  "temperature": 23.0},
        {"sensor": "A", "event_time": base + 62,  "temperature": 21.5},
        {"sensor": "A", "event_time": base + 80,  "temperature": 24.0},
        {"sensor": "B", "event_time": base + 10,  "temperature": 19.0},
        {"sensor": "B", "event_time": base + 55,  "temperature": 20.5},
        {"sensor": "B", "event_time": base + 70,  "temperature": 18.5},
    ]
    
    print(f"\nBase timestamp: {base}")
    print(f"Window size: 60 seconds\n")
    
    # Assign to windows
    windows = defaultdict(list)
    for e in events:
        wk = assign_window(e["event_time"])
        windows[wk].append(e["temperature"])
        print(f"Event t={e['event_time']} (window {wk}) -> {e['temperature']} C")
    
    # Display results
    print(f"\nRESULTS BY WINDOW:")
    print("-" * 40)
    for wk, temps in sorted(windows.items()):
        avg = sum(temps) / len(temps)
        print(f"Window [{wk} - {wk+60}]: average={avg:.1f} C ({len(temps)} events)")
    
    print("\nKey concept: Each event falls into exactly ONE window")
    print("  (calculated by integer division event_time // window_size)")

if __name__ == "__main__":
    demo_tumbling_window()
