from loguru import logger
import sys

# Configuração básica do Loguru
logger.remove()  # Remove configurações padrão para evitar duplicação
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
