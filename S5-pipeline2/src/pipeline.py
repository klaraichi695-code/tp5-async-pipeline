import queue
import threading
import logging


class Pipeline:
    """Orchestre les queues et les threads du pipeline IoT."""

    def __init__(self, maxsize: int = 50):
        self.main_queue = queue.Queue(maxsize=maxsize)
        self.dead_letter_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.threads = []

    def shutdown(self, timeout: float = 10):
        """Arrêt propre : signale l'arrêt et attend tous les threads."""
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=timeout)
            if t.is_alive():
                logging.warning(f"Thread {t.name} n'a pas terminé dans le délai imparti.")