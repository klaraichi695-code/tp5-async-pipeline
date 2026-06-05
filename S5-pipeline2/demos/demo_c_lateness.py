"""
Demo C: Lateness Management (out-of-order events)
Shows how to handle events arriving after window closure
"""
import time

WINDOW_SIZE = 60
ALLOWED_LATENESS = 120  # seconds tolerance

def classify_event(event_time: float, watermark_current: float, window_end: float) -> str:
    """
    Classify event based on lateness relative to window
    
    Policies:
    - on-time: arrived before window closure
    - late-accepted: lateness < allowed_lateness
    - too-late-dropped: lateness > allowed_lateness
    """
    window_start = window_end - WINDOW_SIZE
    
    if event_time >= window_start:
        if watermark_current < window_end:
            return "ON-TIME (before closure)"
    
    lateness = watermark_current - window_end
    if lateness <= ALLOWED_LATENESS:
        return f"LATE-ACCEPTED (lateness={lateness:.0f}s <= {ALLOWED_LATENESS}s)"
    return f"TOO-LATE-DROPPED (lateness={lateness:.0f}s > {ALLOWED_LATENESS}s)"

def demo_lateness():
    print("\n" + "="*60)
    print("DEMO C: Lateness Management (out-of-order events)")
    print("="*60)
    
    base = 1000
    print(f"\nConfiguration:")
    print(f"   - Window size: {WINDOW_SIZE}s")
    print(f"   - Allowed lateness: {ALLOWED_LATENESS}s")
    print(f"   - Window: [{base} - {base+WINDOW_SIZE})")
    
    scenarios = [
        (base + 45, base + 50, "Scenario 1: Watermark just after window"),
        (base + 45, base + 130, "Scenario 2: Watermark moderately after"),
        (base + 45, base + 250, "Scenario 3: Watermark far after"),
        (base + 15, base + 30, "Scenario 4: On-time event"),
    ]
    
    print(f"\nSCENARIO ANALYSIS:")
    print("-" * 60)
    
    for event_time, watermark, description in scenarios:
        window_end = base + WINDOW_SIZE
        result = classify_event(event_time, watermark, window_end)
        print(f"\n{description}:")
        print(f"   Event t={event_time}, watermark={watermark}")
        print(f"   -> {result}")
    
    print("\nKey concepts:")
    print("   1. Watermark = temporal cursor advancing with max(event_time)")
    print("   2. Window closes when watermark >= window_end")
    print("   3. Lateness = trade-off between accuracy and result latency")

if __name__ == "__main__":
    demo_lateness()
