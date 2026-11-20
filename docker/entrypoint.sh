#!/usr/bin/env bash
# e-oficinas - entrypoint de producao (Coolify)
# Mensagens em ASCII puro: evita problema de encoding no container.
set -e

echo "==> e-oficinas iniciando (ON_DOCKER=1)"

# 1) Espera o MySQL ficar disponivel (e garante que o banco existe)
echo "==> Aguardando MySQL em ${DB_HOST:-db}:${DB_PORT:-3306}..."
python <<'PYEOF'
import os, time, sys
import MySQLdb

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "")
name = os.environ.get("DB_NAME", "eoficinas_db")
timeout = int(os.environ.get("DB_WAIT_SECONDS", "60"))

start = time.time()
while True:
    try:
        conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, connect_timeout=5)
        cur = conn.cursor()
        try:
            cur.execute(
                "CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" % name
            )
            conn.commit()
        except Exception:
            # Banco ja criado pelo proprio container MySQL (MYSQL_DATABASE)
            # ou o usuario de app nao tem privilegio de CREATE: nao e problema.
            pass
        conn.close()
        print("==> MySQL pronto (%.1fs)" % (time.time() - start))
        break
    except Exception as exc:
        if time.time() - start > timeout:
            print("==> ERRO: MySQL indisponivel apos %ss: %s" % (timeout, exc), file=sys.stderr)
            sys.exit(1)
        time.sleep(2)
PYEOF

# 2) Migracoes
echo "==> Aplicando migracoes..."
python manage.py migrate --noinput

# 3) Arquivos estaticos (WhiteNoise)
echo "==> Coletando arquivos estaticos..."
python manage.py collectstatic --noinput

# 4) Superusuario opcional (se DJANGO_SUPERUSER_* estiver definido e nao existir)
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  echo "==> Verificando superusuario '${DJANGO_SUPERUSER_USERNAME}'..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL:-admin@example.com}', '${DJANGO_SUPERUSER_PASSWORD}')
    print('Superusuario criado.')
else:
    print('Superusuario ja existe; ignorando.')
" || echo "==> Aviso: nao foi possivel criar superusuario (seguindo mesmo assim)."
fi

# 5) Servidor WSGI
echo "==> Subindo Gunicorn em 0.0.0.0:${PORT:-8000}..."
exec gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
