"""
Jira client wrapper.

Lazy-init and return None when credentials are missing so the rest of
the pipeline can still run without publishing (original code crashed
on import when .env wasn't configured).
"""
import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from jira import JIRA

from app.utils.logger import log_warning, log_error


load_dotenv()


@lru_cache(maxsize=1)
def get_jira() -> Optional[JIRA]:
    url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL") or os.getenv("JIRA_USERNAME")
    token = os.getenv("JIRA_API_TOKEN")

    if not all([url, email, token]):
        log_warning(
            "JIRA credentials missing — skipping Jira/Xray publishing. "
            "Set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env to enable."
        )
        return None

    try:
        return JIRA(server=url, basic_auth=(email, token))
    except Exception as e:
        log_error("JIRA client", e)
        return None
