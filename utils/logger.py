
import logging

# Logger 설정
logging.basicConfig(
    level=logging.INFO,  # INFO, WARNING, ERROR 레벨 출력
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("stair_game")


