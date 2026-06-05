"""
Demo D: Checkpointing (state save and restore)
Shows how to persist state to survive crashes
"""
import json
import pathlib
import time

def demo_checkpoint():
    print("\n" + "="*60)
    print("DEMO D: Checkpointing (Save/Restore State)")
    print("="*60)
    
    # Initial state
    state = {
        "sensor_A": {"count": 5, "sum_temp": 112.5, "avg": 22.5},
        "sensor_B": {"count": 3, "sum_temp": 57.0, "avg": 19.0},
        "sensor_C": {"count": 2, "sum_temp": 43.0, "avg": 21.5}
    }
    watermark = 1700000100.0
    checkpoint_path = "checkpoints/state.json"
    
    print("\nPHASE 1: SAVE CHECKPOINT")
    print("-" * 40)
    print(f"State before save: {len(state)} sensors")
    print(f"Watermark: {watermark}")
    
    # Save checkpoint
    pathlib.Path("checkpoints").mkdir(exist_ok=True)
    payload = {
        "watermark": watermark,
        "state": state,
        "timestamp": time.time()
    }
    pathlib.Path(checkpoint_path).write_text(json.dumps(payload, indent=2))
    print("Checkpoint saved to 'checkpoints/state.json'")
    
    # Simulate crash
    print("\nPHASE 2: SIMULATE CRASH")
    print("-" * 40)
    state = {}
    watermark = 0
    print("CRASH! All in-memory data lost")
    print(f"State after crash: {state}")
    print(f"Watermark after crash: {watermark}")
    
    # New events during crash
    new_events = [
        ("sensor_A", 23.0),
        ("sensor_D", 20.0),
    ]
    print(f"\nNew events received during crash: {new_events}")
    
    # Restore from checkpoint
    print("\nPHASE 3: RESTORE FROM CHECKPOINT")
    print("-" * 40)
    data = json.loads(pathlib.Path(checkpoint_path).read_text())
    state = data["state"]
    watermark = data["watermark"]
    print(f"State restored: {len(state)} sensors")
    print(f"Watermark restored: {watermark}")
    
    # Process new events
    print("\nPHASE 4: PROCESS NEW EVENTS")
    print("-" * 40)
    for sensor, temp in new_events:
        if sensor not in state:
            state[sensor] = {"count": 0, "sum_temp": 0, "avg": 0}
        state[sensor]["count"] += 1
        state[sensor]["sum_temp"] += temp
        state[sensor]["avg"] = state[sensor]["sum_temp"] / state[sensor]["count"]
        print(f"   {sensor}: +{temp} C -> avg={state[sensor]['avg']:.1f} C")
    
    print("\nFINAL STATE AFTER RECOVERY:")
    print("-" * 40)
    for sid, st in sorted(state.items()):
        print(f"   {sid}: count={st['count']}, avg={st['avg']:.1f} C")
    
    print("\nKey concepts:")
    print("   1. Checkpoint = snapshot of state at time T")
    print("   2. After crash, resume from last checkpoint")
    print("   3. Events between checkpoint and crash = possible loss (at-least-once)")
    print("   4. Exactly-once requires transactions or idempotence")

if __name__ == "__main__":
    demo_checkpoint()
