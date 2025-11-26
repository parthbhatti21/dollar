#!/usr/bin/env python3
"""
Dollar Assistant GUI Application
A simple GUI wrapper that runs the Dollar Assistant and allows you to stop it by closing the window.
"""

import sys
import os
import threading
import time
from pathlib import Path
import platform

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'agent'))

# Request microphone permissions on macOS
if platform.system() == 'Darwin':
    try:
        import objc
        from AppKit import NSBundle, NSMicrophoneUsageDescription
        
        # Set microphone usage description
        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.infoDictionary()
            if info:
                info['NSMicrophoneUsageDescription'] = 'Dollar Assistant needs microphone access to detect wake words and listen to your voice commands.'
    except ImportError:
        # PyObjC not available, but that's okay - Info.plist will handle it
        pass
    except Exception as e:
        # Ignore errors - permissions will be requested when audio is accessed
        pass

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    print("Error: tkinter is not available. Please install it:")
    print("  macOS: tkinter should be included with Python")
    print("  Linux: sudo apt-get install python3-tk")
    print("  Windows: tkinter should be included with Python")
    sys.exit(1)

from main import DollarAssistant

class DollarApp:
    """GUI Application for Dollar Assistant."""
    
    def __init__(self):
        """Initialize the GUI and assistant."""
        self.assistant = None
        self.assistant_thread = None
        self.running = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Dollar Assistant")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center the window on screen
        self.center_window()
        
        # Create UI
        self.create_ui()
        
        # Start the assistant (it will handle microphone initialization)
        self.start_assistant()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="💰 Dollar Assistant",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Starting...",
            font=("Helvetica", 12)
        )
        self.status_label.pack()
        
        # Status indicator (circle)
        self.status_canvas = tk.Canvas(
            status_frame,
            width=20,
            height=20,
            highlightthickness=0
        )
        self.status_canvas.pack(pady=5)
        self.status_indicator = self.status_canvas.create_oval(
            5, 5, 15, 15,
            fill="gray",
            outline=""
        )
        
        # Wake word detection indicator
        self.wake_detected_label = ttk.Label(
            status_frame,
            text="",
            font=("Helvetica", 10, "bold"),
            foreground="green"
        )
        self.wake_detected_label.pack(pady=5)
        
        # Info text
        self.info_text_var = tk.StringVar()
        self.info_text_var.set("""
Dollar Assistant is running in the background.

👂 Listening for wake word: "dollar jack"

To stop the assistant, simply close this window.
        """.strip())
        self.info_label = ttk.Label(
            main_frame,
            textvariable=self.info_text_var,
            font=("Helvetica", 10),
            justify=tk.CENTER
        )
        self.info_label.pack(pady=20)
        
        # Instructions
        instructions = """
💡 Say "dollar jack" followed by your command
   Examples:
   • "dollar jack" → "play music"
   • "dollar jack" → "open YouTube"
   • "dollar jack" → "set timer for 5 minutes"
        """
        instructions_label = ttk.Label(
            main_frame,
            text=instructions.strip(),
            font=("Helvetica", 9),
            justify=tk.LEFT,
            foreground="gray"
        )
        instructions_label.pack(pady=10, padx=20)
        
        # Add a button to test microphone access
        test_mic_button = ttk.Button(
            main_frame,
            text="Test Microphone Access",
            command=self.test_microphone_access
        )
        test_mic_button.pack(pady=10)
    
    def test_microphone_access(self):
        """Test microphone access and request permissions if needed."""
        self.update_status("Testing microphone...", "yellow")
        
        try:
            import pyaudio
            # Create a separate PyAudio instance for testing (don't interfere with main stream)
            test_audio = pyaudio.PyAudio()
            
            # Try to open a test stream - this will trigger permission request
            try:
                test_stream = test_audio.open(
                    rate=16000,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=512
                )
                test_stream.start_stream()
                
                # Read a small chunk to ensure it's actually working
                test_stream.read(512, exception_on_overflow=False)
                
                test_stream.stop_stream()
                test_stream.close()
                # Only terminate the test instance, not the main one
                test_audio.terminate()
                
                self.update_status("✅ Microphone access granted!", "green")
                self.root.after(2000, lambda: self.update_status("Running - Listening...", "green"))
                
            except OSError as e:
                error_msg = str(e).lower()
                if 'permission' in error_msg or 'denied' in error_msg:
                    self.update_status("❌ Microphone permission denied", "red")
                    detailed_msg = """Microphone permission denied!

Please:
1. Open System Settings → Privacy & Security → Microphone
2. Find 'Dollar Assistant' or 'Python' in the list
3. Enable the toggle

Then click 'Test Microphone Access' again."""
                    self.info_text_var.set(detailed_msg)
                else:
                    self.update_status(f"Error: {str(e)}", "red")
                test_audio.terminate()
            except Exception as e:
                self.update_status(f"Error testing microphone: {str(e)}", "red")
                try:
                    test_audio.terminate()
                except:
                    pass
        except ImportError:
            self.update_status("pyaudio not available", "red")
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
    
    def update_status(self, status_text, color="green"):
        """Update the status label and indicator."""
        self.status_label.config(text=status_text)
        self.status_canvas.itemconfig(
            self.status_indicator,
            fill=color
        )
        self.root.update()
    
    def on_wake_word_detected(self):
        """Callback when wake word is detected - update GUI."""
        if self.root.winfo_exists():
            self.root.after(0, lambda: self.wake_detected_label.config(text="🎤 Wake word detected!"))
            # Clear after 3 seconds
            self.root.after(3000, lambda: self.wake_detected_label.config(text=""))
    
    def start_assistant(self):
        """Start the Dollar Assistant in a separate thread."""
        def run_assistant():
            try:
                self.update_status("Initializing...", "yellow")
                # Disable signal handlers since we're in a thread
                # Pass callback to get notified when wake word is detected
                self.assistant = DollarAssistant(
                    enable_signal_handlers=False,
                    wake_word_callback=self.on_wake_word_detected
                )
                
                # Check if wake word detector initialized properly
                if not self.assistant.wake_word.audio_stream:
                    error_msg = "Microphone not accessible. Please grant microphone permissions."
                    detailed_msg = """Microphone permission required!

To fix this:
1. Open System Settings → Privacy & Security → Microphone
2. Find 'Dollar Assistant' or 'Python' in the list
3. Enable the toggle

Or:
1. Quit this app
2. Re-launch it
3. Click 'Allow' when prompted"""
                    
                    self.update_status(error_msg, "red")
                    self.root.after(0, lambda: self.info_text_var.set(detailed_msg))
                    print(f"ERROR: {error_msg}", file=sys.stderr)
                    print(f"Wake word method: {self.assistant.wake_word.method}", file=sys.stderr)
                    return
                
                # Verify audio stream is actually active and keep it alive
                try:
                    if hasattr(self.assistant.wake_word.audio_stream, 'is_active'):
                        if not self.assistant.wake_word.audio_stream.is_active():
                            print("WARNING: Audio stream is not active, attempting to start...", file=sys.stderr)
                            try:
                                self.assistant.wake_word.audio_stream.start_stream()
                            except Exception as e:
                                print(f"ERROR: Could not start audio stream: {e}", file=sys.stderr)
                                error_msg = f"Failed to start audio stream: {str(e)}"
                                self.update_status(error_msg, "red")
                                return
                    
                    # Keep a reference to the audio stream to prevent garbage collection
                    # Store it as an instance variable
                    self._audio_stream_ref = self.assistant.wake_word.audio_stream
                    self._audio_ref = self.assistant.wake_word.audio
                    
                    print(f"✅ Audio stream initialized and active: {self.assistant.wake_word.audio_stream.is_active() if hasattr(self.assistant.wake_word.audio_stream, 'is_active') else 'unknown'}")
                except Exception as e:
                    print(f"ERROR: Audio stream check failed: {e}", file=sys.stderr)
                    error_msg = f"Audio stream error: {str(e)}"
                    self.update_status(error_msg, "red")
                    return
                
                self.running = True
                wake_method = self.assistant.wake_word.method
                status_msg = f"Running - Listening for '{wake_method}' wake word..."
                self.update_status(status_msg, "green")
                
                # Update info text with wake word info
                wake_word_phrase = "dollar jack" if wake_method == "porcupine" else "dollar jack"
                info_text = f"""
Dollar Assistant is running in the background.

👂 Listening for wake word: "{wake_word_phrase}"
Method: {wake_method}

💡 Say "dollar jack" clearly to activate

To stop the assistant, simply close this window.
                """.strip()
                self.root.after(0, lambda: self.info_text_var.set(info_text))
                
                print(f"✅ Dollar Assistant started (wake word method: {wake_method})")
                print("👂 Listening for wake word...")
                print("💡 Say 'dollar jack' to activate")
                print(f"🔍 Audio stream active: {self.assistant.wake_word.audio_stream.is_active() if hasattr(self.assistant.wake_word.audio_stream, 'is_active') else 'unknown'}")
                
                # Start the main loop
                self.assistant.run()
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.update_status(error_msg, "red")
                print(f"Error running assistant: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
            finally:
                self.running = False
                # Close window if assistant stops
                if self.root.winfo_exists():
                    self.root.after(0, self.root.destroy)
        
        self.assistant_thread = threading.Thread(target=run_assistant, daemon=True)
        self.assistant_thread.start()
    
    def on_closing(self):
        """Handle window close event - stop the assistant gracefully."""
        if self.running and self.assistant:
            self.update_status("Stopping...", "orange")
            # Stop the assistant
            self.assistant.running = False
            # Call cleanup if available
            if hasattr(self.assistant, 'cleanup'):
                try:
                    self.assistant.cleanup()
                except Exception as e:
                    print(f"Error during cleanup: {e}", file=sys.stderr)
            # Wait a moment for graceful shutdown
            time.sleep(0.5)
        
        # Destroy the window
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        """Start the GUI main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()


def main():
    """Entry point."""
    app = DollarApp()
    app.run()


if __name__ == "__main__":
    main()

