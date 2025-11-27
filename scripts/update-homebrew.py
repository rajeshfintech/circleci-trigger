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
    url "https://files.pythonhosted.org/packages/54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz"
    sha256 "d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
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

