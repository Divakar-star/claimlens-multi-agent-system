"""SQLite access: escalation queue, decisions, and the daily request counter.

Why SQLite: zero setup, single file, survives a container restart if mounted.
No ORM and no migration framework -- the schema is small enough to read.
Implemented in Phase 5 (the daily counter lands earlier, in Phase 3).
"""
