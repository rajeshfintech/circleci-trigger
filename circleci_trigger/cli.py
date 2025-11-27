#!/usr/bin/env python3
import argparse, sys, os, requests
from .config import CIRCLECI_TOKEN_ENV_VAR, ORG, VCS, IAC_REPO, K8S_REPO

def run_init():
    print("🔧 CircleCI Trigger Initialization Wizard\n")

    values = {}

    values["circleci_token_env_var"] = (
        input("Environment variable for CircleCI token [CIRCLECI_TOKEN]: ").strip()
        or "CIRCLECI_TOKEN"
    )

    values["org"] = input("Organization (ORG): ").strip()
    values["vcs"] = input("VCS provider (bitbucket/github): ").strip()
    values["iac_repo"] = input("Repo name for IAC pipelines: ").strip()
    values["k8s_repo"] = input("Repo name for K8S pipelines: ").strip()

    from .config import save_config
    path = save_config(values)

    print("\n✅ Config saved to:", path)
    print("Make sure your token is exported:")
    print(f"  export {values['circleci_token_env_var']}=\"your-token-here\"\n")


def trigger_pipeline(repo, param_name, param_value):
    token = os.environ.get(CIRCLECI_TOKEN_ENV_VAR)
    if not token:
        print(f"Missing token: export {CIRCLECI_TOKEN_ENV_VAR}='yourtoken'")
        sys.exit(1)
    url = f"https://circleci.com/api/v2/project/{VCS}/{ORG}/{repo}/pipeline"
    headers = {"Circle-Token": token, "Content-Type": "application/json"}
    body = {"branch": "main", "parameters": {param_name: param_value}}
    r = requests.post(url, json=body, headers=headers)
    if r.status_code != 201:
        print("Error:", r.text); sys.exit(1)
    print("Triggered:", r.json()["id"])

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--iac", action="store_true")
    p.add_argument("--k8s", action="store_true")
    p.add_argument("--prefix"); p.add_argument("--repo-name")
    p.add_argument("--jira"); p.add_argument("--hash")
    p.add_argument("--init", action="store_true", help="Initialize config file")
    a = p.parse_args()
    if a.init:
        run_init(); 
        return
    cfg = load_config()
    if not a.iac and not a.k8s:
        c = input("iac or k8s? ").strip()
        a.iac = (c=="iac"); a.k8s = (c=="k8s")
    if a.iac:
        pre = a.prefix or input("PREFIX:")
        repo = a.repo_name or input("REPO:")
        jira = a.jira or input("JIRA:")
        tag = f"{pre.upper()}.{repo}.{jira}"
        trigger_pipeline(IAC_REPO, "TAG", tag)
    else:
        env = a.prefix or input("ENV:")
        repo = a.repo_name or input("REPO:")
        h = a.hash or input("HASH:")
        new = f"{env.upper()}.{repo}.{h}"
        trigger_pipeline(K8S_REPO, "NEW", new)

