import os
import yaml

CONFIG_PATH = os.path.expanduser("~/.circleci-trigger/config.yml")

DEFAULT_CONFIG = {
    "circleci_token_env_var": "CIRCLECI_TOKEN",
    "org": None,
    "vcs": None,
    "iac_repo": None,
    "k8s_repo": None,
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_PATH}\n"
            "Please create it with required values."
        )

    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f) or {}

    # merge with defaults
    final = DEFAULT_CONFIG.copy()
    final.update(cfg)

    # Validate required fields
    required = ["org", "vcs", "iac_repo", "k8s_repo"]
    missing = [k for k in required if not final.get(k)]
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")

    return final

