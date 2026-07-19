# Handwritten Ground-Truth Test Set for DriveWise Evaluation

TEST_SET = [
    # --- Hyundai Alcazar (2025) ---
    {
        "brand": "Hyundai",
        "model": "Alcazar",
        "question": "What engine options are available for the Hyundai Alcazar?",
        "ground_truth": "The Hyundai Alcazar is available with two engine options: a 1.5 l Turbo GDi Petrol engine and a 1.5 l U2 CRDi Diesel engine.",
        "expected_section": "engine_performance"
    },
    {
        "brand": "Hyundai",
        "model": "Alcazar",
        "question": "What safety features are standard across all variants of the Hyundai Alcazar?",
        "ground_truth": "Standard safety features on the Hyundai Alcazar include 6 airbags, Electronic Stability Control (ESC), Vehicle Stability Management (VSM), Hill-Start Assist Control (HAC), All-wheel disc brakes, ABS with EBD, and ISOFIX child seat mounts.",
        "expected_section": "safety"
    },
    {
        "brand": "Hyundai",
        "model": "Alcazar",
        "question": "Does the Hyundai Alcazar have a sunroof?",
        "ground_truth": "Yes, the Hyundai Alcazar features a voice-enabled Smart Panoramic Sunroof.",
        "expected_section": "interior_comfort"
    },
    {
        "brand": "Hyundai",
        "model": "Alcazar",
        "question": "What is the seating capacity options for the Hyundai Alcazar?",
        "ground_truth": "The Hyundai Alcazar is offered in both 6-seater (with captain seats in the second row) and 7-seater configurations.",
        "expected_section": "dimensions"
    },
    {
        "brand": "Hyundai",
        "model": "Alcazar",
        "question": "What is the screen size of the infotainment system in the Alcazar?",
        "ground_truth": "The Hyundai Alcazar features a 26.03 cm (10.25\") HD touchscreen infotainment system integrated with a 26.03 cm (10.25\") digital cluster.",
        "expected_section": "infotainment_connectivity"
    },

    # --- Kia Seltos (2026) ---
    {
        "brand": "Kia",
        "model": "Seltos",
        "question": "What safety features are included in the Kia Seltos ADAS Level 2?",
        "ground_truth": "Kia Seltos ADAS Level 2 features include Forward Collision-Avoidance Assist, Lane Keep Assist, Lane Departure Warning, Blind-Spot Collision-Avoidance Assist, Rear Cross-Traffic Collision-Avoidance Assist, Smart Cruise Control with Stop & Go, and High Beam Assist.",
        "expected_section": "safety"
    },
    {
        "brand": "Kia",
        "model": "Seltos",
        "question": "What is the fuel tank capacity of the Kia Seltos?",
        "ground_truth": "The Kia Seltos has a fuel tank capacity of 50 litres.",
        "expected_section": "mileage_fuel_efficiency"
    },
    {
        "brand": "Kia",
        "model": "Seltos",
        "question": "What transmission options are available with the 1.5 l Turbo Petrol engine on Seltos?",
        "ground_truth": "The 1.5 l Turbo Petrol engine on the Seltos is paired with a 6-speed iMT (intelligent Manual Transmission) or a 7-speed DCT (Dual Clutch Transmission).",
        "expected_section": "engine_performance"
    },
    {
        "brand": "Kia",
        "model": "Seltos",
        "question": "Does the Seltos offer a premium sound system?",
        "ground_truth": "Yes, higher-spec variants of the Kia Seltos offer a Bose Premium 8-Speaker sound system.",
        "expected_section": "infotainment_connectivity"
    },
    {
        "brand": "Kia",
        "model": "Seltos",
        "question": "What are the key dimensions (length, width, height, and wheelbase) of the Seltos?",
        "ground_truth": "The Kia Seltos has a length of 4365 mm, a width of 1800 mm, a height of 1620 mm (with roof rails), and a wheelbase of 2610 mm.",
        "expected_section": "dimensions"
    },

    # --- Tata Harrier (2025) ---
    {
        "brand": "Tata",
        "model": "Harrier",
        "question": "What engine powers the Tata Harrier and what are its power specs?",
        "ground_truth": "The Tata Harrier is powered by the Kryotec 2.0 L Turbocharged Diesel engine, producing 170 PS (125 kW) of power at 3750 rpm and 350 Nm of torque at 1750-2500 rpm.",
        "expected_section": "engine_performance"
    },
    {
        "brand": "Tata",
        "model": "Harrier",
        "question": "What is the safety rating and platform of the Tata Harrier?",
        "ground_truth": "The Tata Harrier is built on the OMEGARC platform (Optimal Modular Efficient Global Advanced Architecture) derived from Land Rover's D8 platform, and has received a 5-star safety rating from Global NCAP.",
        "expected_section": "safety"
    },
    {
        "brand": "Tata",
        "model": "Harrier",
        "question": "What is the boot space of the Tata Harrier?",
        "ground_truth": "The Tata Harrier has a boot space capacity of 445 Litres, which can be expanded to 815 Litres with the second-row seats folded.",
        "expected_section": "dimensions"
    },
    {
        "brand": "Tata",
        "model": "Harrier",
        "question": "What is the size of the touchscreen infotainment system in the Tata Harrier?",
        "ground_truth": "The Tata Harrier features a 31.24 cm (12.3 inch) Harman Touchscreen Infotainment system on its higher variants.",
        "expected_section": "infotainment_connectivity"
    },
    {
        "brand": "Tata",
        "model": "Harrier",
        "question": "Does the Tata Harrier have ventilated seats?",
        "ground_truth": "Yes, the Tata Harrier offers ventilated seats for both driver and co-driver in its top-spec variants.",
        "expected_section": "interior_comfort"
    }
]
