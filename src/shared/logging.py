import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application.

    MUST NOT have external dependencies.
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
