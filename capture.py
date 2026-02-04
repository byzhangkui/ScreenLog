import datetime
import os
import threading
import time
import mss
import mss.tools

class CaptureEngine:
    def __init__(self, save_dir="captures", interval_ms=500):
        self.save_dir = save_dir
        self.interval_ms = interval_ms
        self.running = False
        self.thread = None
        self.region = None # {'top': 0, 'left': 0, 'width': 100, 'height': 100}

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def set_region(self, x, y, width, height):
        # mss region format: {'top': int, 'left': int, 'width': int, 'height': int}
        # Note: On macOS with Retina displays, coordinates might need scaling. 
        # For now we assume standard coordinates or that mss handles it if we pass the right ones.
        self.region = {'top': int(y), 'left': int(x), 'width': int(width), 'height': int(height)}

    def start(self):
        if self.running:
            return
        if not self.region:
            print("Region not set!")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def _capture_loop(self):
        with mss.mss() as sct:
            while self.running:
                start_time = time.time()
                
                try:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = os.path.join(self.save_dir, f"capture_{timestamp}.png")
                    
                    # Capture
                    sct_img = sct.grab(self.region)
                    
                    # Save to file
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
                    # print(f"Saved {filename}")

                except Exception as e:
                    print(f"Error capturing screenshot: {e}")

                # Calculate sleep time to maintain interval
                elapsed = (time.time() - start_time) * 1000
                sleep_time = max(0, (self.interval_ms - elapsed) / 1000.0)
                time.sleep(sleep_time)
