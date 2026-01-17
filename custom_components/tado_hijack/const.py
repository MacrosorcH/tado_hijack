"""Constants for Tado Hijack."""

from typing import Final

DOMAIN: Final = "tado_hijack"

# Library Specifics
TADO_VERSION_PATCH: Final = "0.2.2"
TADO_USER_AGENT: Final = f"HomeAssistant/{TADO_VERSION_PATCH}"

# Configuration Keys
CONF_REFRESH_TOKEN: Final = "refresh_token"
CONF_SLOW_POLL_INTERVAL: Final = "slow_poll_interval"

# Default Intervals
DEFAULT_SCAN_INTERVAL: Final = 3600
DEFAULT_SLOW_POLL_INTERVAL: Final = 24  # Hours

# Minimums
MIN_SCAN_INTERVAL: Final = 30
MIN_SLOW_POLL_INTERVAL: Final = 1  # Hour

# Timing & Logic
DEBOUNCE_COOLDOWN_S: Final = 5
OPTIMISTIC_GRACE_PERIOD_S: Final = 30
PROTECTION_MODE_TEMP: Final = 5.0  # Minimum safe temperature for manual override
SLOW_POLL_CYCLE_S: Final = 86400  # 24 Hours in seconds

# Service Names
SERVICE_MANUAL_POLL: Final = "manual_poll"
SERVICE_RESUME_ALL_SCHEDULES: Final = "resume_all_schedules"
