import os
import hashlib
import requests
from github import Github

PACKAGE = "circleci-trigger"
REPO = "rajeshfintech/circleci-trigger"
TAP_REPO = os.environ["HOMEBREW_TAP_REPO"]
VERSION = os.environ["VERSION_FROM_GITHUB"]

DEPENDENCIES = [
    "PyYAML",
    "requests",
    "urllib3",
    "charset-normalizer",
    "idna",
    "certifi"
]


def get_pypi_sdist_info(package):
    """Fetch version, URL & SHA256 for a package's sdist tarball."""
    url = f"https://pypi.org/pypi/{package}/json"
    r = requests.get(url)
    if r.status_code != 200:
        raise SystemExit(f"❌ Failed to fetch PyPI metadata for {package}")

    data = r.json()
    version = data["info"]["version"]

    # Find sdist (source tarball)
    sdist = next(
        (x for x in data["urls"] if x["packagetype"] == "sdist"),
        None
    )

    if not sdist:
        raise SystemExit(f"❌ No sdist found for {package}")

    return {
        "name": package,
        "version": version,
        "url": sdist["url"],
        "sha256": sdist["digests"]["sha256"],
    }


def generate_resource_block(info):
    """Generate a Homebrew resource block."""
    return f"""
  resource "{info['name']}" do
    url "{info['url']}"
    sha256 "{info['sha256']}"
  end
"""


def main():
    print("📦 Building Homebrew formula dynamically...")

    # Detect tarball built from your package
    dist_files = [f for f in os.listdir("dist") if f.endswith(".tar.gz")]
    if not dist_files:
        raise SystemExit("❌ ERROR: No tar.gz file found in dist/")
    tarball = dist_files[0]
    print(f"🔍 Using tarball: {tarball}")

    # Compute SHA256 of your package tarball
    sha256_hash = hashlib.sha256()
    with open(f"dist/{tarball}", "rb") as f:
        sha256_hash.update(f.read())
    tarball_sha = sha256_hash.hexdigest()

    download_url = (
        f"https://github.com/{REPO}/releases/download/v{VERSION}/{tarball}"
    )

    # Resolve dependencies
    print("🔍 Resolving dependencies from PyPI...")
    resources = ""
    for dep in DEPENDENCIES:
        info = get_pypi_sdist_info(dep)
        print(f"  ✓ {dep} {info['version']}")
        resources += generate_resource_block(info)

    # Construct Homebrew formula
    formula = f"""class CircleciTrigger < Formula
  include Language::Python::Virtualenv

  desc "CircleCI trigger CLI"
  homepage "https://github.com/{REPO}"
  url "{download_url}"
  sha256 "{tarball_sha}"
  license "MIT"

  depends_on "python@3.12"
{resources}
  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{{bin}}/circleci-trigger", "--help"
  end
end
"""

    print("📝 Updating tap repo:", TAP_REPO)

    gh = Github(os.environ["GH_TOKEN"])
    tap = gh.get_repo(TAP_REPO)

    try:
        existing = tap.get_contents("Formula/circleci-trigger.rb")
        tap.update_file(
            "Formula/circleci-trigger.rb",
            f"Update to v{VERSION}",
            formula,
            existing.sha
        )
        print("✅ Updated existing formula.")
    except Exception:
        tap.create_file(
            "Formula/circleci-trigger.rb",
            f"Create formula v{VERSION}",
            formula
        )
        print("✅ Created new formula.")


if __name__ == "__main__":
    main()

