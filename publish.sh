#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REMOTE="origin"
DEFAULT_BRANCH="main"

cd "${PROJECT_DIR}"

printf '[i] Black Bear secure publish helper\n'
printf '[i] This script does not store your token on disk.\n\n'

if ! command -v git >/dev/null 2>&1; then
  printf '[!] git is not installed.\n' >&2
  exit 1
fi

if [[ ! -d .git ]]; then
  git init
  git branch -M "${DEFAULT_BRANCH}"
fi

read -r -p 'GitHub username: ' GITHUB_USERNAME
read -r -p 'Commit name [leave empty to keep current git config]: ' COMMIT_NAME
read -r -p 'Commit email [leave empty to keep current git config]: ' COMMIT_EMAIL
read -r -s -p 'GitHub token (input hidden): ' GITHUB_TOKEN
printf '\n'
read -r -p 'Commit message [Initial Black Bear release]: ' COMMIT_MESSAGE
COMMIT_MESSAGE="${COMMIT_MESSAGE:-Initial Black Bear release}"
read -r -p 'Remote name [origin]: ' REMOTE_NAME
REMOTE_NAME="${REMOTE_NAME:-$DEFAULT_REMOTE}"
read -r -p 'Branch [main]: ' BRANCH_NAME
BRANCH_NAME="${BRANCH_NAME:-$DEFAULT_BRANCH}"
read -r -p 'Remote URL [https://github.com/mohammad1390555/sfdsgfd.git]: ' REMOTE_URL
REMOTE_URL="${REMOTE_URL:-https://github.com/mohammad1390555/sfdsgfd.git}"

if [[ -n "${COMMIT_NAME}" ]]; then
  git config user.name "${COMMIT_NAME}"
fi

if [[ -n "${COMMIT_EMAIL}" ]]; then
  git config user.email "${COMMIT_EMAIL}"
fi

if ! git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  git remote add "${REMOTE_NAME}" "${REMOTE_URL}"
else
  git remote set-url "${REMOTE_NAME}" "${REMOTE_URL}"
fi

if [[ -n "$(git status --porcelain)" ]]; then
  git add .
  git commit -m "${COMMIT_MESSAGE}" || true
fi

ASKPASS_FILE="$(mktemp)"
cleanup() {
  rm -f "${ASKPASS_FILE}"
  unset GITHUB_TOKEN
  unset GIT_ASKPASS
}
trap cleanup EXIT

cat > "${ASKPASS_FILE}" <<'EOF'
#!/usr/bin/env bash
case "$1" in
  *Username*) printf '%s' "${GITHUB_USERNAME}" ;;
  *Password*) printf '%s' "${GITHUB_TOKEN}" ;;
  *) printf '%s' "" ;;
esac
EOF
chmod 700 "${ASKPASS_FILE}"

export GITHUB_USERNAME
export GITHUB_TOKEN
export GIT_ASKPASS="${ASKPASS_FILE}"
export GIT_TERMINAL_PROMPT=0

printf '\n[+] Pushing to %s (%s)\n' "${REMOTE_NAME}" "${BRANCH_NAME}"
git push -u "${REMOTE_NAME}" "${BRANCH_NAME}"
printf '[+] Publish complete.\n'
