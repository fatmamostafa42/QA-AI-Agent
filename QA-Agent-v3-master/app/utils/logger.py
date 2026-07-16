import time


# =========================================================
# BASIC LOGGING
# =========================================================

def log_step(title: str):

    print("\n" + "=" * 60)
    print(title.upper())
    print("=" * 60)


def log_info(message: str):

    print(f"[INFO] {message}")


def log_success(message: str):

    print(f"[SUCCESS] {message}")


def log_warning(message: str):

    print(f"[WARNING] {message}")


def log_error(agent_name: str, error: Exception):

    print(f"\n[{agent_name}] ERROR")
    print(str(error))


# =========================================================
# AGENT LOGGING
# =========================================================

def log_agent_start(agent_name: str):

    print(f"\n[START] {agent_name}")


def log_agent_end(agent_name: str, start_time: float):

    elapsed = round(time.time() - start_time, 2)

    print(f"[END] {agent_name} ({elapsed} sec)")


def log_agent_skip(agent_name: str):

    print(f"[SKIPPED] {agent_name}")


# =========================================================
# TIMER CONTEXT MANAGER
# =========================================================

class Timer:

    def __init__(self, name="Operation"):

        self.name = name

    def __enter__(self):

        self.start = time.time()

        print(f"\n[START] {self.name}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        elapsed = round(time.time() - self.start, 2)

        print(f"[END] {self.name} ({elapsed} sec)")