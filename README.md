# tp5-async-pipeline
## Objectif

Construire un pipeline producteur/consommateur asynchrone avec backpressure, retry, dead-letter queue et scale-out automatique.

---

## Prérequis

- Python 3.11+

---

## Installation

```bash
cd TPs/TP5_Async_Pipeline
# Pas de dépendances externes
Exécution
bash
python src/main.py
Structure
text
TP5_Async_Pipeline/
├── src/
│   ├── main.py           # Orchestration
│   ├── messages.py       # EventMessage (enveloppe)
│   ├── producers.py      # Générateur de rafales
│   ├── workers.py        # Validation + retry/DLQ
│   ├── metrics.py        # Métriques + dashboard
│   ├── storage.py        # CSVStorage thread-safe
│   └── pipeline.py       # Queue + stop_event
├── logs/                 # Journaux
└── outputs/              # Résultats
Paramètres
Paramètre	Valeur
Producteurs	3
Workers initiaux	2
Workers max	5
Taille queue	50 (backpressure)
Bursts par producteur	5 × 30 messages
Taux d'invalides	~10%
Max retries	3
Résultats
Indicateur	Valeur
Messages produits	450
Acceptés	~413
DLQ	~37
Retries	~74
Débit	~69 msg/s
Fichiers générés :

outputs/valid_readings.csv

outputs/dead_letters.json

outputs/aggregation.json

logs/pipeline.log

Dashboard
text
[DASHBOARD] backlog=  47 | success=  89 | fail=  2 | retry= 11 | rate=  38.2 msg/s | latency= 1205.7ms
Indicateur	Signification
backlog	Messages en attente
success	Messages traités avec succès
fail	Messages en DLQ
retry	Tentatives de re-traitement
rate	Débit (msg/s)
latency	Latence moyenne (ms)
Logique retry/DLQ
Situation	Action
Validation OK	Écriture CSV
Validation KO + attempts < 3	Remise en queue
Validation KO + attempts = 3	→ DLQ
Queue pleine au retry	→ DLQ directement
Scale-out automatique
Si backlog > 40, un nouveau worker est démarré (max 5).

Sortie console (final)
text
=======================================================
  RÉSULTAT FINAL
=======================================================
  Messages traités avec succès : 413
  Messages échoués (DLQ)       : 37
  Retries effectués            : 74
  Débit moyen                  : 69.2 msg/s
  Latence moyenne              : 45.3 ms
  Durée totale                 : 6.2 s
=======================================================

 Toutes les assertions passent !
Difficultés rencontrées
Backpressure : queue bornée pour éviter l'accumulation mémoire

Thread-safety : Lock pour les métriques et le stockage CSV

Arrêt propre : stop_event + join(timeout) pour éviter les deadlocks

