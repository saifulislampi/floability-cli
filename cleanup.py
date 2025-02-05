# cleanup.py
"""
Manages subprocess cleanup. Now we send SIGINT to each process so they can do
their own shutdown (e.g. vine_factory removing workers), then we fallback to
terminate() if they're still alive.
"""

import signal
import sys
import time

class CleanupManager:
    """
    Tracks subprocesses we need to clean up on Ctrl+C or program exit.
    """
    def __init__(self):
        self.subprocesses = []

    def register_subprocess(self, proc):
        """
        Register a Popen subprocess so that we can clean it up later.
        """
        self.subprocesses.append(proc)

    def cleanup(self):
        """
        1) Send SIGINT to each subprocess so they can do their own cleanup.
        2) Wait briefly. Any process still running is terminated.
        """
        print("[cleanup] Sending SIGINT to all subprocesses so they can do their own cleanup...")

        # 1) Send SIGINT
        for proc in self.subprocesses:
            if proc.poll() is None:  # still running
                print(f"[cleanup] SIGINT -> pid={proc.pid}")
                try:
                    proc.send_signal(signal.SIGINT)
                except Exception as e:
                    print(f"[cleanup] Warning: could not send SIGINT to pid={proc.pid}: {e}")

        # 2) Give them a moment to exit
        time.sleep(2)

        # 3) Anyone still running, we call terminate()
        for proc in self.subprocesses:
            if proc.poll() is None:
                print(f"[cleanup] Process pid={proc.pid} still alive; calling terminate()")
                try:
                    proc.terminate()
                except Exception as e:
                    print(f"[cleanup] Warning: could not terminate pid={proc.pid}: {e}")

        # Optional: final wait to ensure they're gone
        for proc in self.subprocesses:
            try:
                proc.wait(timeout=2)
            except:
                pass

        print("[cleanup] All subprocesses cleaned up.")


def install_signal_handlers(cleanup_manager: CleanupManager):
    """
    Installs a signal handler so that Ctrl+C (SIGINT) or SIGTERM triggers
    the CleanupManager's cleanup(), then exits.
    """
    import signal

    def signal_handler(sig, frame):
        print(f"[cleanup] Caught signal {sig}, initiating cleanup...")
        cleanup_manager.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

