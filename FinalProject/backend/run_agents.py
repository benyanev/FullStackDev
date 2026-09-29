"""Run the agent world simulation — a separate process from the web server.

    python run_agents.py            # run forever, one action every AGENT_INTERVAL_SECONDS
    python run_agents.py --once     # do a single action and exit (for testing)
    python run_agents.py --once comment   # force a specific action

Why a separate process (and not inside Flask)?  The Flask dev server's
reloader starts the app twice, and a production server runs several
workers, so a scheduler inside the web app would make every bot act 2-4
times per tick.  In Docker this becomes its own small container.
"""

import sys
import time
from datetime import datetime

from core.config import AGENT_INTERVAL_SECONDS
from services.agent_service import ACTIONS, run_agent_tick


# Bots write emojis; the Windows console (cp1252) can't print them by default
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def log(message):
    print(f'[{datetime.now():%H:%M:%S}] {message}', flush=True)


def main():
    args = sys.argv[1:]
    forced_action = next((a for a in args if a in ACTIONS), None)

    if '--once' in args:
        log(run_agent_tick(forced_action))
        return

    log(f'Agents running — one action every {AGENT_INTERVAL_SECONDS}s (Ctrl+C to stop)')
    while True:
        try:
            log(run_agent_tick(forced_action))
        except Exception as e:  # keep the simulation alive (e.g. DB restarted)
            log(f'tick failed: {e!r}')
        time.sleep(AGENT_INTERVAL_SECONDS)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('Agents stopped.')
