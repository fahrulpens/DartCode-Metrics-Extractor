
from .common import count_loc
from .methods import number_of_methods, max_number_of_params
from .complexity import cyclomatic_complexity
from .nesting import max_nesting_depth
from .fields import number_of_fields
from .comments import comment_ratio
from .widgets import number_of_widgets, max_widget_nesting, child_chain_max_depth

from .side_effects import (
    setstate_call_count,
    provider_bloc_mutation_count,
    field_assignment_count,
    mutable_collection_mod_count,
    api_call_count,
)

from .runtime_effects import (
    database_call_count,     # DbC
    sync_io_count,           # SyncIO
    image_codec_count,       # ImgC
    async_await_ui_count,    # AsyncUI
    timer_stream_init_count, # TmrStr
)

__all__ = ["METRICS", "ALIASES"]

METRICS = {
    "loc":  ("LoC",  count_loc),
    "nom":  ("NoM",  number_of_methods),
    "nop":  ("NoP",  max_number_of_params),
    "cc":   ("CC",   cyclomatic_complexity),
    "mnd":  ("MND",  max_nesting_depth),
    "nof":  ("NoF",  number_of_fields),
    "cr":   ("CR",   comment_ratio),
    "now":  ("NoW",  number_of_widgets),
    "mnw":  ("MNW",  max_widget_nesting),
    "sccl": ("SCCL", child_chain_max_depth),
    
    "sstc": ("sStC", setstate_call_count),
    "pbm":  ("PBM",  provider_bloc_mutation_count),
    "fac":  ("FAC",  field_assignment_count),
    "mc":   ("MC",   mutable_collection_mod_count),
    "api":  ("API",  api_call_count),

    "dbc":    ("DbC",    database_call_count),
    "syncio": ("SyncIO", sync_io_count),
    "imgc":   ("ImgC",   image_codec_count),
    "asyncui":("AsyncUI",async_await_ui_count),
    "tmrstr": ("TmrStr", timer_stream_init_count),
}

ALIASES = {
    "line of code": "loc", "line_of_code": "loc", "line-of-code": "loc",
    "number of methods": "nom", "number_of_methods": "nom", "number-of-methods": "nom",
    "number of parameters": "nop", "number_of_parameters": "nop", "number-of-parameters": "nop",
    "cyclomatic complexity": "cc", "cyclomatic_complexity": "cc", "cyclomatic-complexity": "cc",
    "maximum nesting depth": "mnd", "maximum_nesting_depth": "mnd", "maximum-nesting-depth": "mnd",
    "number of fields": "nof", "number_of_fields": "nof", "number-of-fields": "nof",
    "comment ratio": "cr", "comment_ratio": "cr", "comment-ratio": "cr",
    "number of widget": "now", "number_of_widget": "now", "number-of-widget": "now",
    "maximum nesting widget": "mnw", "maximum_nesting_widget": "mnw", "maximum-nesting-widget": "mnw",
    "max widget tree depth": "mnw", "max_widget_tree_depth": "mnw",
    "single-child wrapper chain length": "sccl",
    "single_child_wrapper_chain_len": "sccl",
    "single-child-wrapper-chain-length": "sccl",

    "setstate call count": "sstc", "setstate": "sstc", "ssetstate": "sstc",
    "provider/bloc mutation count": "pbm", "provider bloc mutation count": "pbm",
    "field assignment count": "fac",
    "mutable collection modification count": "mc", "mutable collection count": "mc",
    "api call count": "api", "network call count": "api",

    "database call count": "dbc", "db call count": "dbc",
    "synchronous io count": "syncio", "sync io count": "syncio",
    "image codec call count": "imgc", "image decode count": "imgc",
    "async/await in ui": "asyncui", "await count": "asyncui",
    "timer/stream init count": "tmrstr", "timer stream init count": "tmrstr",
}
