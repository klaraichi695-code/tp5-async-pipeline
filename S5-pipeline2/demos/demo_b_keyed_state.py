"""
Demo B: Keyed State (per-sensor aggregation)
Shows how to maintain state per key without storing full history
"""
from dataclasses import dataclass

@dataclass
class SensorState:
    """Aggregated state for a sensor"""
    count: int = 0
    sum_temp: float = 0.0
    min_temp: float = float('inf')
    max_temp: float = float('-inf')

    def update(self, temp: float):
        """Update state with a new temperature reading"""
        self.count += 1
        self.sum_temp += temp
        self.min_temp = min(self.min_temp, temp)
        self.max_temp = max(self.max_temp, temp)

    @property
    def avg(self) -> float:
        """Average temperature"""
        return self.sum_temp / self.count if self.count else 0

def demo_keyed_state():
    print("\n" + "="*60)
    print("DEMO B: Keyed State (per-sensor average)")
    print("="*60)
    
    # Event stream (sensor, temperature)
    events = [
        ("sensor_A", 22.0), ("sensor_B", 18.5),
        ("sensor_A", 23.5), ("sensor_C", 21.0),
        ("sensor_A", 21.0), ("sensor_B", 19.0),
        ("sensor_B", 20.5), ("sensor_C", 22.5),
    ]
    
    # State per sensor (only 3 states for 8 events!)
    states: dict[str, SensorState] = {}
    
    print("\nPROCESSING EVENT BY EVENT:")
    print("-" * 50)
    
    for sensor_id, temp in events:
        if sensor_id not in states:
            states[sensor_id] = SensorState()
            print(f"New sensor detected: {sensor_id}")
        
        states[sensor_id].update(temp)
        print(f"   {sensor_id}: +{temp} C -> count={states[sensor_id].count}, avg={states[sensor_id].avg:.1f} C")
    
    # Final results
    print(f"\nFINAL RESULTS:")
    print("-" * 40)
    for sid, st in sorted(states.items()):
        print(f"Sensor {sid}:")
        print(f"   - Samples: {st.count}")
        print(f"   - Average: {st.avg:.1f} C")
        print(f"   - Min/Max: {st.min_temp:.1f} C / {st.max_temp:.1f} C")
    
    print("\nKey concept: Memory usage = O(num_keys) not O(num_events)")
    print(f"   (8 events -> only 3 states stored)")

if __name__ == "__main__":
    demo_keyed_state()
