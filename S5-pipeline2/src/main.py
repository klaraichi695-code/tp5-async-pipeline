import threading
import logging
import os
import json
import queue

from messages import EventMessage
from producers import burst_producer
from workers import worker_loop
from metrics import PipelineMetrics, monitor_loop
from storage import CSVStorage
from pipeline import Pipeline


def main():
    # Créer les répertoires (depuis src/, les dossiers sont créés un niveau au-dessus)
    os.makedirs("../logs", exist_ok=True)
    os.makedirs("../outputs", exist_ok=True)

    # Logging : fichier + console simultanément
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("../logs/pipeline.log", mode="w"),
            logging.StreamHandler(),
        ]
    )

    logging.info("=== Démarrage du pipeline IoT ===")

    # Composants principaux
    pipe = Pipeline(maxsize=50)
    metrics = PipelineMetrics()
    storage = CSVStorage("../outputs/valid_readings.csv")

    # Fabrique de workers (réutilisée pour le scale-out)
    def make_worker(name: str) -> threading.Thread:
        return threading.Thread(
            target=worker_loop,
            args=(pipe.main_queue, pipe.dead_letter_queue, storage,
                  metrics, pipe.stop_event, name),
            name=name,
            daemon=True,
        )

    # Lancer 2 workers initiaux
    for i in range(1, 3):
        t = make_worker(f"Worker-{i}")
        t.start()
        pipe.threads.append(t)
        logging.info(f"Worker-{i} démarré")

    # Lancer le moniteur avec scale-out activé
    t_mon = threading.Thread(
        target=monitor_loop,
        args=(pipe.main_queue, metrics, pipe.stop_event),
        kwargs=dict(
            interval=2,
            pipeline=pipe,
            max_workers=5,
            worker_factory=make_worker,
        ),
        name="Monitor",
        daemon=True,
    )
    t_mon.start()
    pipe.threads.append(t_mon)

    # Lancer 3 producteurs
    prod_threads = []
    for i in range(1, 4):
        t = threading.Thread(
            target=burst_producer,
            args=(pipe.main_queue, f"Prod-{i}", 5, 30, 0.5),
            name=f"Prod-{i}",
        )
        t.start()
        prod_threads.append(t)
        logging.info(f"Prod-{i} démarré")

    # Attendre la fin de tous les producteurs
    for t in prod_threads:
        t.join()
    logging.info("Tous les producteurs ont terminé.")

    # Attendre que la queue se vide complètement
    pipe.main_queue.join()
    logging.info("Queue principale vidée.")

    # Arrêt propre
    pipe.shutdown(timeout=5)

    # Rapport final
    snap = metrics.snapshot()
    logging.info("=== RÉSULTAT FINAL ===")
    logging.info(f"Messages traités avec succès : {snap['success']}")
    logging.info(f"Messages échoués (DLQ)       : {snap['failures']}")
    logging.info(f"Retries effectués             : {snap['retries']}")
    logging.info(f"Débit moyen                   : {snap['rate_per_sec']} msg/s")
    logging.info(f"Latence moyenne               : {snap['avg_latency_ms']} ms")
    logging.info(f"Durée totale                  : {snap['elapsed_sec']} s")

    # Sauvegarder la dead-letter queue
    dead = []
    while not pipe.dead_letter_queue.empty():
        try:
            msg = pipe.dead_letter_queue.get_nowait()
            dead.append(msg.to_dict())
        except queue.Empty:
            break

    with open("../outputs/dead_letters.json", "w") as f:
        json.dump(dead, f, indent=2, default=str)
    logging.info(f"Dead-letters sauvegardés : {len(dead)}")

    # Agrégation par capteur
    agg = storage.aggregate()
    logging.info(f"Agrégation par capteur :\n{json.dumps(agg, indent=2)}")

    # Assertions de base
    assert snap["success"] > 0, "Aucun message traité avec succès !"
    assert len(dead) == snap["failures"], "Incohérence DLQ !"
    assert storage.count == snap["success"], "Incohérence stockage !"
    logging.info("Toutes les assertions passent.")


if __name__ == "__main__":
    main()