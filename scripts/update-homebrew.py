import os, hashlib
from github import Github

version = os.environ["VERSION_FROM_GITHUB"]
repo = "rajeshfintech/circleci-trigger"

# Auto-detect source tarball
dist_files = [f for f in os.listdir("dist") if f.endswith(".tar.gz")]

if not dist_files:
    raise SystemExit("❌ ERROR: No .tar.gz file found in dist/. Build likely failed.")

tarball = dist_files[0]
print(f"📦 Detected source tarball: {tarball}")

download_url = f"https://github.com/{repo}/releases/download/v{version}/{tarball}"

# Compute sha256
sha256_hash = hashlib.sha256()
with open(f"dist/{tarball}", "rb") as f:
    sha256_hash.update(f.read())
sha = sha256_hash.hexdigest()
print(f"🔐 SHA256: {sha}")

formula = f"""class CircleciTrigger < Formula
  include Language::Python::Virtualenv

  desc "CircleCI trigger CLI"
  homepage "https://github.com/{repo}"
  url "{download_url}"
  sha256 "{sha}"
  license "MIT"

  depends_on "python@3.12"

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/95/45/ba8fb6a0e8e5a0d28abc89c6f0ca6c58410820cb38faae5f68539f3e41c0/PyYAML-6.0.2.tar.gz"
    sha256 "2e4c0f6e38b1d34cbb7a4ca93782bb2b5005fd464729725dcf2d44c3a37f0e6f"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/90/8e/33cb83bdbfaa9a90bf34e66b4a79e927651c01fb9b31c8ed6dfa8185728a/requests-2.32.3.tar.gz"
    sha256 "68d7dedbb5c1e5c23bf3a4dd63ee39073d28a3fcc594a5a2175b4832c75b7f03"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{{bin}}/circleci-trigger", "--help"
  end
end
"""

# Push to tap repo
g = Github(os.environ["GH_TOKEN"])
tap_repo = g.get_repo(os.environ["HOMEBREW_TAP_REPO"])

try:
    existing = tap_repo.get_contents("Formula/circleci-trigger.rb")
    tap_repo.update_file(
        "Formula/circleci-trigger.rb",
        f"Update formula to v{version}",
        formula,
        existing.sha
    )
except:
    tap_repo.create_file(
        "Formula/circleci-trigger.rb",
        f"Create formula for v{version}",
        formula
    )

