"""Local YMCA Ghana branches.

Region placement follows the town each branch sits in. Names are stored
exactly as supplied by YMCA Ghana. Coordinates are approximate town centres
so the admin map can place branches that have a known location.
"""

from typing import List, Optional, Tuple

# id, region_id, name, address, lat, lng
GhanaBranch = Tuple[str, str, str, str, Optional[float], Optional[float]]

GHANA_BRANCHES: List[GhanaBranch] = [
    # Eastern
    ("br_koforidua", "reg_eastern", "Koforidua", "Koforidua, Eastern Region", 6.0941, -0.2591),
    ("br_mampong", "reg_eastern", "Mampong", "Mampong, Eastern Region", 5.9167, -0.1367),
    ("br_asaman", "reg_eastern", "Asaman", "Asaman, Eastern Region", 5.8606, -0.6669),
    ("br_nudu", "reg_eastern", "Nudu", "Nudu, Eastern Region", 6.1100, -0.2800),
    ("br_oda", "reg_eastern", "Oda", "Oda, Eastern Region", 5.9268, -0.9855),
    ("br_mpraeso", "reg_eastern", "Mpraeso", "Mpraeso, Eastern Region", 6.5836, -0.7347),
    ("br_dzumapor", "reg_eastern", "Dzumapor", "Dzumapor, Eastern Region", 6.1472, -0.3478),
    ("br_osenease", "reg_eastern", "Osenease", "Osenease, Eastern Region", 6.0834, -0.2675),
    ("br_apadwa", "reg_eastern", "Apadwa", "Apadwa, Eastern Region", 6.1456, -0.4667),
    ("br_donkorkrom", "reg_eastern", "Donkorkrom", "Donkorkrom, Eastern Region", 7.0586, -0.0986),
    # Greater Accra
    ("br_madina", "reg_greater_accra", "Madina", "Madina, Greater Accra", 5.6830, -0.1666),
    ("br_tema", "reg_greater_accra", "Tema", "Tema, Greater Accra", 5.6698, -0.0166),
    ("br_bawaleshie", "reg_greater_accra", "Bawaleshie", "Bawaleshie, Greater Accra", 5.6408, -0.1534),
    ("br_mamprobi", "reg_greater_accra", "Mamprobi", "Mamprobi, Greater Accra", 5.5347, -0.2306),
    ("br_harbor_city", "reg_greater_accra", "Harbor City", "Harbor City, Greater Accra", 5.6415, 0.0166),
    ("br_accra_city", "reg_greater_accra", "Accra City", "Accra City, Greater Accra", 5.5600, -0.2050),
    ("br_prampram", "reg_greater_accra", "Prampram", "Prampram, Greater Accra", 5.7167, 0.1167),
    # Ashanti
    ("br_kumasi", "reg_ashanti", "Kumasi", "Kumasi, Ashanti Region", 6.6885, -1.6244),
    ("br_konongo", "reg_ashanti", "Konongo", "Konongo, Ashanti Region", 6.6167, -1.2167),
    ("br_mborso", "reg_ashanti", "Mborso", "Mborso, Ashanti Region", 6.6554, -1.1071),
    ("br_wawase", "reg_ashanti", "Wawase", "Wawase, Ashanti Region", 6.4667, -1.7167),
    ("br_basa", "reg_ashanti", "Basa", "Basa, Ashanti Region", 7.7877, -0.4149),
    # Western
    ("br_takoradi", "reg_western", "Takoradi", "Takoradi, Western Region", 4.8845, -1.7554),
    ("br_ketan", "reg_western", "Ketan", "Ketan, Western Region", 4.9180, -1.7680),
    ("br_sekendi", "reg_western", "Sekendi", "Sekendi, Western Region", 4.9340, -1.7137),
    ("br_takwa", "reg_western", "Takwa", "Takwa, Western Region", 5.3018, -1.9952),
    ("br_tanokurom", "reg_western", "Tanokurom", "Tanokurom, Western Region", 4.8930, -1.7700),
    # Volta
    ("br_ho", "reg_volta", "Ho", "Ho, Volta Region", 6.6008, 0.4713),
    ("br_amfoata_kyebi", "reg_volta", "Amfoata Kyebi", "Amfoata Kyebi, Volta Region", 6.7319, 0.3878),
    ("br_amfoaga", "reg_volta", "Amfoaga", "Amfoaga, Volta Region", 6.8875, 0.2767),
]

RETIRED_BRANCH_IDS = (
    "br_hq_accra",
    "br_ttc_accra",
    "br_regional_accra",
    "br_regional_ashanti",
    "br_regional_eastern",
    "br_regional_volta",
    "br_regional_western",
    "br_vti_takoradi",
)
