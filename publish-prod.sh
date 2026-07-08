#!/bin/bash
set -e

SERVER="root@165.22.16.53"
REMOTE_DEPLOY="/server/pimpamtest.nualart.cat/prod/deploy.sh"

DEV_BRANCH="develop"
PROD_BRANCH="main"

COMMIT_MESSAGE="$1"

if [ -z "$COMMIT_MESSAGE" ]; then
  echo "Has d'escriure un missatge de commit."
  echo "Ús:"
  echo "./publish-prod.sh \"Canvis\""
  exit 1
fi

echo "==> Comprovant que som al repo..."
git status >/dev/null

echo "==> Comprovant remot..."
git remote -v | grep -q "jaumet/PimPamTest" || {
  echo "ERROR: Aquest no sembla el repo de PimPamTest."
  git remote -v
  exit 1
}

echo "==> Canviant a $DEV_BRANCH..."
git checkout "$DEV_BRANCH"

echo "==> Afegint canvis..."
git add .

echo "==> Fent commit si hi ha canvis..."
if git diff --cached --quiet; then
  echo "No hi ha canvis per commitejar a $DEV_BRANCH."
else
  git commit -m "$COMMIT_MESSAGE"
fi

echo "==> Pujant $DEV_BRANCH..."
git push origin "$DEV_BRANCH"

echo "==> Canviant a $PROD_BRANCH..."
git checkout "$PROD_BRANCH"

echo "==> Actualitzant $PROD_BRANCH local des de GitHub..."
git pull --ff-only origin "$PROD_BRANCH"

echo "==> Alineant $PROD_BRANCH amb $DEV_BRANCH..."
git merge --ff-only "$DEV_BRANCH"

echo "==> Pujant $PROD_BRANCH..."
git push origin "$PROD_BRANCH"

echo "==> Tornant a $DEV_BRANCH..."
git checkout "$DEV_BRANCH"

echo "==> Executant deploy al servidor..."
ssh -tt "$SERVER" "$REMOTE_DEPLOY"

echo "==> Publicació completada."
