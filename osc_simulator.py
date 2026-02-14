"""
OSC Data Simulator for EEG Neurofeedback Game
Simulates Muse 2 EEG data stream for testing without hardware

Generates realistic EEG waveforms with different concentration states
that can be cycled through or controlled via keyboard input.
"""

import time
import numpy as np
from pythonosc import udp_client
import argparse

# Configuration
OSC_IP = "127.0.0.1"
OSC_PORT = 5000
SAMPLING_RATE = 256  # Muse 2 sampling rate (Hz)
CHANNELS = 4  # TP9, AF7, AF8, TP10

# Concentration states with different EEG characteristics
STATES = {
    'low': {
        'name': 'Low Focus (Mind Wandering)',
        'theta': 1.5,    # High theta (distraction)
        'alpha': 1.2,    # Moderate alpha (relaxed)
        'smr': 0.8,      # Low SMR
        'beta': 0.7,     # Low beta (poor attention)
    },
    'medium': {
        'name': 'Medium Focus (Calm Attention)',
        'theta': 1.0,    # Baseline theta
        'alpha': 1.0,    # Baseline alpha
        'smr': 1.3,      # Moderate SMR increase
        'beta': 1.2,     # Moderate beta increase
    },
    'high': {
        'name': 'High Focus (Peak Concentration)',
        'theta': 0.7,    # Low theta (no wandering)
        'alpha': 0.8,    # Lower alpha (active)
        'smr': 1.8,      # High SMR (focused)
        'beta': 1.6,     # High beta (engaged)
    }
}


class EEGSimulator:
    def __init__(self, osc_ip: str, osc_port: int):
        self.client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        self.current_state = 'medium'
        self.time = 0
        self.noise_phase = np.random.rand(CHANNELS) * 2 * np.pi
        
    def generate_eeg_sample(self) -> list:
        """
        Generate one sample of realistic EEG data for all channels
        Simulates different frequency components based on current state
        """
        state = STATES[self.current_state]
        t = self.time / SAMPLING_RATE
        
        samples = []
        for ch in range(CHANNELS):
            # Base signal components (in microvolts)
            signal = 0.0
            
            # Delta (0.5-4 Hz) - deep sleep, not relevant for focus
            signal += 20 * np.sin(2 * np.pi * 2 * t + self.noise_phase[ch])
            
            # Theta (4-8 Hz) - drowsiness, mind wandering
            signal += 40 * state['theta'] * np.sin(2 * np.pi * 6 * t + self.noise_phase[ch] * 2)
            
            # Alpha (8-13 Hz) - relaxed awareness
            signal += 60 * state['alpha'] * np.sin(2 * np.pi * 10 * t + self.noise_phase[ch] * 3)
            
            # SMR (12-15 Hz) - focused attention
            signal += 35 * state['smr'] * np.sin(2 * np.pi * 13 * t + self.noise_phase[ch] * 4)
            
            # Beta (13-30 Hz) - active thinking, concentration
            signal += 45 * state['beta'] * np.sin(2 * np.pi * 20 * t + self.noise_phase[ch] * 5)
            
            # Gamma (30-44 Hz) - peak mental activity (subtle)
            signal += 15 * state['beta'] * 0.5 * np.sin(2 * np.pi * 35 * t + self.noise_phase[ch] * 6)
            
            # Add realistic noise
            noise = np.random.randn() * 10
            signal += noise
            
            # Frontal channels (AF7, AF8) should be stronger for concentration
            if ch in [1, 2]:  # AF7, AF8
                signal *= 1.2
            
            samples.append(float(signal))
        
        self.time += 1
        return samples
    
    def set_state(self, state: str):
        """Change concentration state"""
        if state in STATES:
            self.current_state = state
            print(f"\n>>> Switched to: {STATES[state]['name']}")
        else:
            print(f"Unknown state: {state}")
    
    def send_sample(self):
        """Generate and send one EEG sample via OSC"""
        sample = self.generate_eeg_sample()
        self.client.send_message("/muse/eeg", sample)
    
    def run_auto_cycle(self, duration: int = 30):
        """
        Automatically cycle through concentration states
        duration: seconds per state
        """
        print(f"\n=== Auto-cycling through states (every {duration}s) ===")
        print("Press Ctrl+C to stop\n")
        
        states_cycle = ['low', 'medium', 'high', 'medium']
        state_idx = 0
        samples_per_state = duration * SAMPLING_RATE
        sample_count = 0
        
        try:
            while True:
                # Check if time to switch state
                if sample_count % samples_per_state == 0:
                    self.set_state(states_cycle[state_idx])
                    state_idx = (state_idx + 1) % len(states_cycle)
                
                self.send_sample()
                sample_count += 1
                
                # Sleep to maintain proper sampling rate
                time.sleep(1.0 / SAMPLING_RATE)
                
                # Progress indicator
                if sample_count % (SAMPLING_RATE * 5) == 0:
                    print(f"Sent {sample_count} samples... (current: {self.current_state})")
                    
        except KeyboardInterrupt:
            print("\n\nSimulator stopped.")
    
    def run_interactive(self):
        """
        Interactive mode - user controls concentration state
        """
        print("\n=== Interactive Mode ===")
        print("Press keys to change concentration state:")
        print("  1 - Low Focus (mind wandering)")
        print("  2 - Medium Focus (calm attention)")
        print("  3 - High Focus (peak concentration)")
        print("  q - Quit")
        print("\nStarting with Medium Focus...")
        print("Streaming EEG data to {}:{}".format(OSC_IP, OSC_PORT))
        
        try:
            # Note: For true interactive keyboard input, you'd want to use a library like `keyboard`
            # For simplicity, this version just streams medium focus continuously
            # User can stop with Ctrl+C
            print("\n(Simple version: streams medium focus continuously)")
            print("For full interactive controls, enhance with keyboard library")
            
            while True:
                self.send_sample()
                time.sleep(1.0 / SAMPLING_RATE)
                
        except KeyboardInterrupt:
            print("\n\nSimulator stopped.")


def main():
    parser = argparse.ArgumentParser(description="EEG Data Simulator for Neurofeedback Game")
    parser.add_argument('--ip', default=OSC_IP, help=f'OSC target IP (default: {OSC_IP})')
    parser.add_argument('--port', type=int, default=OSC_PORT, help=f'OSC target port (default: {OSC_PORT})')
    parser.add_argument('--mode', choices=['auto', 'interactive'], default='auto',
                       help='Simulation mode (default: auto)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Duration per state in auto mode (default: 30s)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("   EEG SIMULATOR - Muse 2 Neurofeedback Game")
    print("="*60)
    print(f"\nTarget: {args.ip}:{args.port}")
    print(f"Sampling Rate: {SAMPLING_RATE} Hz")
    print(f"Channels: {CHANNELS} (TP9, AF7, AF8, TP10)")
    
    simulator = EEGSimulator(args.ip, args.port)
    
    if args.mode == 'auto':
        simulator.run_auto_cycle(duration=args.duration)
    else:
        simulator.run_interactive()


if __name__ == "__main__":
    main()
