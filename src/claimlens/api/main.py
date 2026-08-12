"""FastAPI app: claim submission, review queue, trace viewer, metrics.

Why server-rendered Jinja2 and no frontend framework: the reviewer of this repo
should be able to read the entire UI in one sitting, and `docker run` should
produce a working demo with no build step. Implemented in Phase 5.
"""
