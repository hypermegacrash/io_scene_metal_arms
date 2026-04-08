# Module defining the shaders as understood by PASM

SHADER_INFO = [
    {"name": "oBASE",                         "deprecated": False, "fallback": None},  # 0
    {"name": "cBASE",                         "deprecated": False, "fallback": None},  # 1
    {"name": "tBASE",                         "deprecated": False, "fallback": None},  # 2
    {"name": "obsBASE",                       "deprecated": True,  "fallback": 0},     # 3 -> oBASE
    {"name": "beoBASE",                       "deprecated": True,  "fallback": 0},     # 4 -> oBASE
    {"name": "etbsBASE",                      "deprecated": True,  "fallback": 2},     # 5 -> tBASE
    {"name": "oBASE_LERP_tLAYER",             "deprecated": False, "fallback": None},  # 6
    {"name": "cBASE_LERP_tLAYER",             "deprecated": False, "fallback": None},  # 7
    {"name": "tBASE_LERP_tLAYER",             "deprecated": True,  "fallback": None},  # 8
    {"name": "oBASE_LERP_vLAYER",             "deprecated": False, "fallback": None},  # 9
    {"name": "cBASE_LERP_vLAYER",             "deprecated": False, "fallback": None},  # 10
    {"name": "oBASE_LERP_pLAYER",             "deprecated": False, "fallback": None},  # 11
    {"name": "cBASE_LERP_pLAYER",             "deprecated": False, "fallback": None},  # 12
    {"name": "oBASE_MOD_SHADOWMAP",           "deprecated": True,  "fallback": None},  # 13
    {"name": "cBASE_MOD_SHADOWMAP",           "deprecated": True,  "fallback": None},  # 14
    {"name": "oBASE_ADD_rbENV",               "deprecated": False, "fallback": None},  # 15
    {"name": "etBASE_ADD_rbENV",              "deprecated": False, "fallback": None},  # 16
    {"name": "oBASE_ADD_rbENV_MOD_SHADOWMAP", "deprecated": True,  "fallback": None},  # 17
    {"name": "ADD_BASE",                      "deprecated": False, "fallback": None},  # 18
    {"name": "oBASE_ADD_rbSREFLECT",          "deprecated": False, "fallback": None},  # 19
    {"name": "tBASE_vALPHA",                  "deprecated": True,  "fallback": None},  # 20
    {"name": "LIQUID_ENV",                    "deprecated": False, "fallback": None},  # 21
    {"name": "LIQUID_LAYER_ENV",              "deprecated": False, "fallback": None},  # 22
    {"name": "LIQUID_TEXTURE",                "deprecated": False, "fallback": None},  # 23
    {"name": "LIQUID_MOLTEN_1LAYER",          "deprecated": False, "fallback": None},  # 24
    {"name": "LIQUID_MOLTEN_2LAYER",          "deprecated": False, "fallback": None},  # 25
    {"name": "oBASE_LERP_tLAYER_ADD_rbENV",   "deprecated": False, "fallback": None},  # 26
    {"name": "oBASE_LERP_vLAYER_ADD_rbENV",   "deprecated": False, "fallback": None},  # 27
    {"name": "oBASE_LERP_pLAYER_ADD_rbENV",   "deprecated": False, "fallback": None},  # 28
    {"name": "pBASE",                         "deprecated": False, "fallback": None},  # 29
    {"name": "epbsBASE",                      "deprecated": True,  "fallback": None},  # 30
    {"name": "ADD_vBASE",                     "deprecated": False, "fallback": None},  # 31
]