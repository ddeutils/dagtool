from typing import Any

from .filters import unnested_list
from .macros import get_env, get_var

PLUGINS_FILTERS: dict[str, Any] = {
    "unnested_list": unnested_list,
}
PLUGINS_MACROS: dict[str, Any] = {
    "var": get_var,
    "env": get_env,
}
