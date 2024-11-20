import logging
from util.formatters import LogColors


class ColoredFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.INFO: LogColors.BLUE,
        logging.WARNING: LogColors.ORANGE,
        logging.ERROR: LogColors.RED,
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno, LogColors.RESET)
        message = super().format(record)
        return f"{log_color}{message}{LogColors.RESET}"


formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust the level as needed
logger.addHandler(handler)
