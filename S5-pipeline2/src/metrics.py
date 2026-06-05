import threading
import time
import queue as queue_mod
import logging

class PipelineMetrics:
    """Compteurs thread-safe pour l'observabilité du pipeline."""

    def __init__(self):
        self._lock = threading.Lock()
        self.success = 0
        self.failures = 0
        self.retries = 0
        self.drops = 0
        self.total_latency = 0.0
        self.start_time = time.time()

    def record_success(self, latency: float):
        with self._lock:
            self.success += 1
            self.total_latency += latency

    def record_failure(self):
        with self._lock:
            self.failures += 1

    def record_retry(self):
        with self._lock:
            self.retries += 1

    def record_drop(self):
        with self._lock:
            self.drops += 1

    def snapshot(self) -> dict:
        with self._lock:
            elapsed = time.time() - self.start_time
            rate = self.success / elapsed if elapsed > 0 else 0
            avg_lat = (self.total_latency / self.success) if self.success else 0
            return {
                "success": self.success,
                "failures": self.failures,
                "retries": self.retries,
                "drops": self.drops,
                "rate_per_sec": round(rate, 1),
                "avg_latency_ms": round(avg_lat * 1000, 1),
                "elapsed_sec": round(elapsed, 1),
            }


def monitor_loop(q: queue_mod.Queue, metrics: PipelineMetrics,
                 stop: threading.Event, interval: float = 2,
                 pipeline=None, max_workers: int = 5, worker_factory=None):
    """Dashboard texte + scale-out dynamique si backlog > 80%."""
    worker_count = [2]

    while not stop.is_set():
        s = metrics.snapshot()
        backlog = q.qsize()
        maxsize = q.maxsize if q.maxsize > 0 else 50

        print(
            f"[DASHBOARD] backlog={backlog:>4} | "
            f"success={s['success']:>5} | fail={s['failures']:>3} | "
            f"retry={s['retries']:>3} | "
            f"rate={s['rate_per_sec']:>6.1f} msg/s | "
            f"latency={s['avg_latency_ms']:>7.1f}ms"
        )

        # Scale-out dynamique (bonus)
        if (worker_factory is not None and pipeline is not None
                and backlog > int(maxsize * 0.8)
                and worker_count[0] < max_workers):
            worker_count[0] += 1
            new_name = f"Worker-{worker_count[0]}"
            t = worker_factory(new_name)
            t.start()
            pipeline.threads.append(t)
            logging.warning(f"SCALE-OUT: {new_name} démarré (backlog={backlog})")
            print(f"[SCALE-OUT] {new_name} démarré (backlog={backlog})")

        time.sleep(interval)