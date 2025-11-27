import os
import hashlib
import requests
from github import Github

# Repo config
TAP_REPO = os.environ["HOMEBREW_TAP_REPO"]
GH_TOKEN = os.environ["GH_TOKEN"]

# Find tarball
dist_files = [f for f in os.listdir("dist") if f.endswith(".tar.gz")]
if not dist_files:
    raise SystemExit("No files found in dist/")

tarball = dist_files[0]
version = tarball.split("-")[-1].replace(".tar.gz", "")

# Compute SHA256
sha256_hash = hashlib.sha256()
with open(f"dist/{tarball}", "rb") as f:
    sha256_hash.update(f.read())
sha = sha256_hash.hexdigest()

print(f"Found tarball: {tarball}")
print(f"Version: {version}")
print(f"SHA256: {sha}")

# Construct tarball URL
repo = os.getenv("GITHUB_REPOSITORY")
download_url = f"https://github.com/{repo}/releases/download/v{version}/{tarball}"

# Create/update formula
formula_content = f"""\
class CircleciTrigger < Formula
  include Language::Python::Virtualenv

  desc "CLI to trigger CircleCI pipelines for n1-iac and n1-k8s"
  homepage "https://github.com/{repo}"
  url "{download_url}"
  sha256 "{sha}"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "{{bin}}/circleci-trigger", "--help"
  end
end
"""

# Push to tap repo
g = Github(GH_TOKEN)
tap_repo = g.get_repo(TAP_REPO)

formula_path = "Formula/circleci-trigger.rb"

try:
    existing = tap_repo.get_contents(formula_path)
    tap_repo.update_file(
        formula_path,
        f"Update circleci-trigger to {version}",
        formula_content,
        existing.sha,
        branch="main",
    )
    print("Updated existing formula")

except Exception:
    tap_repo.create_file(
        formula_path,
        f"Create circleci-trigger formula {version}",
        formula_content,
        branch="main",
    )
    print("Created new formula")

