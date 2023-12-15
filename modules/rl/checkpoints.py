from pathlib import Path
import datetime
import os

# UPDATE CHECKPOINT PATHS HERE

# Training mode
TRAINING_CKP = "None"
# TRAINING_CKP = "checkpoints/luigi/2023-12-14T12-37-29/mario_net_47.chkpt"
training_ckp = (
    Path(TRAINING_CKP)
    if os.path.exists(TRAINING_CKP)
    else None
)

# Battle AI mode
# BATTLE_CKP = "None"
BATTLE_CKP = "checkpoints/luigi/2023-12-14T23-51-58/mario_net_1.chkpt"
battle_ai_ckp = (
    Path(BATTLE_CKP)
    if os.path.exists(BATTLE_CKP)
    else None
)