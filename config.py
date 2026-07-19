import os

# Central Configuration for DriveWise

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
CHUNKS_FILE = os.path.join(DATA_DIR, "chunks.jsonl")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
QUERY_LOG_FILE = os.path.join(LOGS_DIR, "query_log.jsonl")
EVAL_DIR = os.path.join(BASE_DIR, "eval")
EVAL_RESULTS_FILE = os.path.join(EVAL_DIR, "eval_results.json")


BROCHURE_CATALOG = [
    {
        "file": "Hyundai_Alcazar_2025.pdf",
        "brand": "Hyundai",
        "model": "Alcazar",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "SUV"
    },
    {
        "file": "Hyundai_Creta.pdf",
        "brand": "Hyundai",
        "model": "Creta",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "SUV"
    },
    {
        "file": "Hyundai_Verna.pdf",
        "brand": "Hyundai",
        "model": "Verna",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "Sedan"
    },
    {
        "file": "Hyundai_i20.pdf",
        "brand": "Hyundai",
        "model": "i20",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "Hatchback"
    },
    {
        "file": "Hyundai_ioniq-5.pdf",
        "brand": "Hyundai",
        "model": "Ioniq 5",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "EV"
    },
    {
        "file": "Kia_Seltos_2026.pdf",
        "brand": "Kia",
        "model": "Seltos",
        "year": 2026,
        "doc_version": "1.0",
        "body_type": "SUV"
    },
    {
        "file": "Kia_Carens-Clavis-EV_2026.pdf",
        "brand": "Kia",
        "model": "Carens-Clavis-EV",
        "year": 2026,
        "doc_version": "1.0",
        "body_type": "EV"
    },
    {
        "file": "Tata_Harrier_2025.pdf",
        "brand": "Tata",
        "model": "Harrier",
        "year": 2025,
        "doc_version": "1.0",
        "body_type": "SUV"
    },
    {
        "file": "Tata_Sierra_2026.pdf",
        "brand": "Tata",
        "model": "Sierra",
        "year": 2026,
        "doc_version": "1.0",
        "body_type": "SUV"
    }
]

SECTION_KEYWORDS = {
    "engine_performance": [
        "engine", "torque", "power", "rpm", "performance", "turbo", "gearbox", "transmission", 
        "clutch", "cylinder", "displacement", "speed", "manual", "automatic", "drive mode", "paddle shift"
    ],
    "mileage_fuel_efficiency": [
        "mileage", "fuel efficiency", "km/l", "kpl", "fuel economy", "fuel tank", "consumption", "diesel", "petrol", "hybrid"
    ],
    "safety": [
        "safety", "airbag", "abs", "ebd", "esc", "adas", "brake", "collision", "lane", "sensor", "camera", 
        "hill assist", "tpms", "seatbelt", "isofix", "crumple zone", "fortress", "stability", "traction control"
    ],
    "dimensions": [
        "dimensions", "length", "width", "height", "wheelbase", "ground clearance", "boot space", 
        "turning radius", "weight", "tyre size", "seating capacity"
    ],
    "interior_comfort": [
        "interior", "seat", "dashboard", "steering", "comfort", "ac", "sunroof", "leather", "ventilated seat", 
        "glove box", "charging", "armrest", "headrest", "cabin", "purifier", "upholstery", "wireless charger"
    ],
    "infotainment_connectivity": [
        "infotainment", "screen", "display", "bluetooth", "android auto", "apple carplay", "speaker", 
        "audio", "navigation", "connected car", "ota update", "bose", "sound system", "touchscreen"
    ],
    "exterior_styling": [
        "exterior", "styling", "grille", "led", "headlamp", "taillamp", "alloy wheel", "roof rail", 
        "bumper", "spoiler", "skid plate", "cladding", "paint", "color", "chrome"
    ],
    "variants_pricing": [
        "variant", "price", "trim", "executive", "prestige", "platinum", "signature", "htx", "gtx", "x-line", 
        "smart", "pure", "adventure", "fearless", "price list", "ex-showroom", "specification sheets", "specifications"
    ]
}
