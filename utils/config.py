"""
Global config values that you can import across modules.
"""
from .logger import get_logger
logger = get_logger(__name__)

# Any other global constants can go here
APP_NAME = "vehicle_ai_agents"
