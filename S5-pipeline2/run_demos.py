#!/usr/bin/env python
"""
Launcher for all streaming demonstrations
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def main():
    
    print("    STREAM PROCESSING DEMONSTRATIONS")
    print("    Windowing | Keyed State | Lateness | Checkpoint")
   
    
    from demos.demo_a_tumbling_window import demo_tumbling_window
    from demos.demo_b_keyed_state import demo_keyed_state
    from demos.demo_c_lateness import demo_lateness
    from demos.demo_d_checkpoint import demo_checkpoint
    
    demo_tumbling_window()
    input("\nPress Enter to continue...")
    
    demo_keyed_state()
    input("\nPress Enter to continue...")
    
    demo_lateness()
    input("\nPress Enter to continue...")
    
    demo_checkpoint()
    
  
    print("    END OF DEMONSTRATIONS")
    

if __name__ == "__main__":
    main()
