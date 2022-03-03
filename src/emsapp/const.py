def N_(msg: str) -> str:
    return msg


COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

ENTRY_FIELDS = [
    N_("date_start"),
    N_("date_end"),
    N_("role"),
    N_("institution"),
    N_("institution_type"),
    N_("location"),
]
DISTRICTS = [
    N_("Broye"),
    N_("Glâne"),
    N_("Gruyère"),
    N_("Lac"),
    N_("Sarine"),
    N_("Singine"),
    N_("Veveyse"),
]

MSG_DURATION = 3000
PLOT_MIN_HEIGHT = 5.0
PLOT_MAX_HEIGHT = 30.0
PLOT_MIN_WIDTH = 5.0
PLOT_MAX_WIDTH = 40.0

ALL_COLUMNS = ENTRY_FIELDS + ["district"]

DATE_OUTPUT_FMT = N_("{dt.day} {dt:%b} {dt.year}")
