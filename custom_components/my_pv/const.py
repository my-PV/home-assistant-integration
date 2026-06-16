"""Constants for the my-PV integration."""

from typing import Final

DOMAIN: Final = "my_pv"

UPDATE_COMMANDS = [
    "check_fwupd",
    "co_fw",
    "firmware_update",
    "force_psupdate",
    "p9s_fw",
    "ps_fw",
]
RESERVED_KEYS = [
    "check_fwupd",
    "coversion",  # codespell:ignore coversion
    "coversionlatest",
    "devmode",
    "firmware_download",
    "firmware_update",
    "fwversion",
    "fwversionlatest",
    "p9s_fw",
    "ps_fw",
    "psversion",
    "psversionlatest",
    "upd_percentage",
    "upd_state",
    "ww1target",
]
