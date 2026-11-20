# 🚀 Deploy no VPS (Hostinger) via Coolify

**Domínio:** `eoficinas.ivcsofthouse.com.br`

Este projeto usa um esqueleto Docker completo para automatizar todo o deploy:

| Arquivo | Função |
|---|---|
| `Dockerfile` | Imagem Python 3.12 + libs do mysqlclient + Gunicorn |
| `docker-compose.yml` | App + MySQL 8 com healthchecks e volumes |
| `docker/entrypoint.sh` | Espera o MySQL → `migrate` → `collectstatic` → superuser opcional → Gunicorn |
| `.env.example` | Modelo de variáveis de ambiente |
| `.dockerignore` / `.gitattributes` | Build limpa e quebras de linha LF |

---

## 1. Preparar o domínio (painel Hostinger)

No DNS do domínio `ivcsofthouse.com.br`, crie o registro:

```
Type: A    Name: eoficinas    Value: <IP do VPS>    TTL: Auto
```

> O Coolify emite o certificado Let's Encrypt automaticamente após o DNS propagar.

## 2. Apontar o Coolify para o repositório

1. No Coolify: **Sources → Add Source → GitHub App** (repo `Ivanildo-Lab/e-oficinas`).
2. **Resources → + New → Public Repository** (ou "Docker Compose").
3. Selecione o repositório e marque **Use Docker Compose** com o arquivo `docker-compose.yml`.
4. Nome do recurso: `eoficinas`.

## 3. Variáveis de ambiente

Em **Resource → Environment Variables**, cadastre:

```env
DJANGO_SECRET_KEY=<gerar com: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=eoficinas.ivcsofthouse.com.br
DJANGO_CSRF_TRUSTED_ORIGINS=https://eoficinas.ivcsofthouse.com.br
DB_NAME=eoficinas_db
DB_USER=eoficinas
DB_PASSWORD=<senha-forte-para-o-banco>
DB_ROOT_PASSWORD=<senha-root-forte>
GUNICORN_WORKERS=3
DJANGO_SUPERUSER_USERNAME=admin        # opcional
DJANGO_SUPERUSER_EMAIL=admin@ivcsofthouse.com.br
DJANGO_SUPERUSER_PASSWORD=<senha-do-admin>  # opcional
```

> O entrypoint espera o MySQL subir (até 60s), cria o banco se não existir, roda as migrações e o `collectstatic` sozinho — nada manual.

## 4. Domínio e HTTPS

1. Na aba **Networks** (ou Domains) do recurso, adicione:
   - `https://eoficinas.ivcsofthouse.com.br`
   - Porta do app: `8000`
2. Salve — o Caddy do Coolify emite o certificado Let's Encrypt automaticamente.

## 5. Deploy

Clique em **Deploy**. O Fluxo automático:

```
git pull → docker build → sobe MySQL → espera healthy → migrate → collectstatic → superuser → Gunicorn
```

## 6. Pós-deploy

```bash
# Criar superusuário (se não usou as variáveis acima)
docker exec -it <container_app> python manage.py createsuperuser

# Backup do banco
docker exec <container_db> mysqldump -uroot -p eoficinas_db > backup_$(date +%F).sql

# Backup da mídia (logos, fotos de produtos, fotos de OS)
docker run --rm -v <nome_do_volume_media>:/data -v $PWD:/backup alpine \
  tar czf /backup/media_$(date +%F).tar.gz -C /data .
```

Acessos:
- Site: `https://eoficinas.ivcsofthouse.com.br`
- Login: `https://eoficinas.ivcsofthouse.com.br/login/`
- Admin: `https://eoficinas.ivcsofthouse.com.br/admin/`

## 7. Deploy automático em pushes

No recurso do Coolify, ative em **Git → Watch Paths / Auto Deploy**: cada `git push` para `main` dispara um novo deploy automático.

---

### Notas de produção

- **Mídia** (logos, fotos de produtos, fotos de OS/assinaturas): volume Docker `media_data` → sobrevive a rebuilds.
- **Estáticos**: servidos pelo WhiteNoise (gzip + cache de 1 ano), sem nginx extra.
- **Banco**: volume Docker `db_data` → MySQL sobrevive a rebuilds. Faça backup periódico.
- O `DEBUG` fica `false` por padrão quando `ON_DOCKER=1`.
- **Dev local**: nada muda — o `.env` local continua valendo (`SECRET_KEY`, `DEBUG`, `DB_HOST=127.0.0.1`).
