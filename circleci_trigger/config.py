import os
import yaml

# FIX: CONFIG_DIR **must** be defined before save_config()
CONFIG_DIR = os.path.expanduser("~/.circleci-trigger")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yml")

DEFAULT_CONFIG = {
    "circleci_token_env_var": "CIRCLECI_TOKEN",
    "org": "",
    "vcs": "",
    "iac_repo": "",
    "k8s_repo": "",
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"❌ Config not found: {CONFIG_PATH}\n"
            "Run: circleci-trigger init"
        )

    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f) or {}

    final = DEFAULT_CONFIG.copy()
    final.update(cfg)
    return final


def save_config(values: dict):
    # FIX: ensure CONFIG_DIR *exists*
    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(values, f)

    return CONFIG_PATH

