from enum import Enum


class Split(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Category(str, Enum):
    DISCOVERY = "discovery"
    FILTERING = "filtering"
    VISUALIZATION = "visualization"
    STATISTICS = "statistics"
    CODE_GENERATION = "code_generation"
    SPATIAL_REASONING = "spatial_reasoning"
    TEMPORAL = "temporal"
    CHANGE_DETECTION = "change_detection"
    MULTIMODAL = "multimodal"
    PLANNING = "planning"

    # ContextGeo task taxonomy retained verbatim.
    SPATIAL_QUERY = "spatial_query"
    SPATIAL_ANALYSIS = "spatial_analysis"
    RASTER_ANALYSIS = "raster_analysis"
    DATA_INTEGRATION = "data_integration"


class Platform(str, Enum):
    GEE = "gee"
    QGIS = "qgis"
    ARCGIS = "arcgis"
    PYTHON = "python"
    WEB = "web"
    GENERAL_GIS = "general_gis"


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    MAP = "map"
    VOICE = "voice"
    TABLE = "table"
    MULTIMODAL = "multimodal"


class DatasetProvider(str, Enum):
    GOOGLE = "google"
    USGS = "usgs"
    ESA = "esa"
    NASA = "nasa"
    FAO = "fao"
    JRC = "jrc"
    OSM = "osm"
    US_CENSUS = "us_census"
    MULTI_SOURCE = "multi_source"
    CUSTOM = "custom"


class OutputType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    CODE = "code"
    IMAGE = "image"
    JSON = "json"
    GEOMETRY = "geometry"
    TABLE = "table"
    WORKFLOW = "workflow"


class Metric(str, Enum):
    EXACT_MATCH = "exact_match"
    KEYWORD_COVERAGE = "keyword_coverage"
    OPERATION_COVERAGE = "operation_coverage"
    OPERATION_PRECISION = "operation_precision"
    OPERATION_RECALL = "operation_recall"
    OPERATION_F1 = "operation_f1"
    HALLUCINATED_OPERATION_RATE = "hallucinated_operation_rate"
    WORKFLOW_ORDER = "workflow_order"
    EXECUTION_SUCCESS = "execution_success"
    CODE_PRESENCE = "code_presence"
    SPATIAL_REASONING = "spatial_reasoning"
    LATENCY = "latency"
    TOKEN_USAGE = "token_usage"
    COST = "cost"


class ReasoningLevel(str, Enum):
    RETRIEVAL = "retrieval"
    FILTERING = "filtering"
    ANALYSIS = "analysis"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    PLANNING = "planning"
    MULTI_STEP = "multi_step"
