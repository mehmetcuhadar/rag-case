'''
Central logging setup (JSON logs later if you want).
Adds request-id middleware later if needed.
'''

import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )