# AUTH SERVICE
Auth service for movies app

## Development

#### Local development
- Install python 3.11 (easy way is [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation))
- Install [poetry](https://python-poetry.org/docs/#installing-with-pipx)
- Run `cd src && poetry install` to create `.venv`
- Activate venv ``. .venv/bin/activate``
- ```cp .env.example .env  # edit if necessary```

#### Generate public and private keys for JWT token
```bash
ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
# Don't add passphrase
openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
```

In `.env` file set variable keys
```dotenv
...

PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA3yE8KAgl/0l+Z9BH4yQ3
Z5DMjcHLIloFgxKwgmUdI/Ntwz1R6I7N0VbacBmfcSh28CnO/o/rHiNugu8Dnd4L
DkuZo8Pwfi0Z1WULgwQX35rePMn87blQPEalo3uxD0RhG+OdSSXe/39h1TyK5bT9
mN4tIESU/OwwTrYE8V4wDwahF8xmuDCBaqjPduhuLQts9/n99GA2j4e2SrKFWDRp
...
l9huqP2OronCt8dHFRB2hvAoFK6Mh9L0JvyfZSWdHprkdHwUkWOwNjQbg01UgYYy
/LyWvuZehG7/0z9QlrictfYnoOb5q0TYea7XgpZcFasuVMrE8C+77dtLs+hUDvsO
OiCZ0I6kysRaNJoLJM6CnekCAwEAAQ==
-----END PUBLIC KEY-----
"

SECRET_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIJKAIBAAKCAgEA3yE8KAgl/0l+Z9BH4yQ3Z5DMjcHLIloFgxKwgmUdI/Ntwz1R
6I7N0VbacBmfcSh28CnO/o/rHiNugu8Dnd4LDkuZo8Pwfi0Z1WULgwQX35rePMn8
7blQPEalo3uxD0RhG+OdSSXe/39h1TyK5bT9mN4tIESU/OwwTrYE8V4wDwahF8xm
uDCBaqjPduhuLQts9/n99GA2j4e2SrKFWDRpJFMh/8W7tiAf16rARIBqbReZ5TJD
...
WVf9052OMbRRpWlL7RU7anPkRvfSiVtCckE5MVxN0fJkaAJQrixXNJ+okzAttLMw
6PrMpLA36qIseFAVYcPBQDUbU9Yn82HAcOdfEhrXGKESe3Ad/LySuehUEAy8w89G
8yk/QRt5pM39kC3Q2Vuyhi4N+dAGnUAbt7pdoG17Uc2/1O96YRUbQknO0uRY1Lvh
5FDmuSQGpjXqDeuVSMXZ29ov3FFhXS1xDDsIfw7U0AIeyt7x8hbEWylOYTY=
-----END RSA PRIVATE KEY-----"

...
```

#### Apply migrations
```shell
cd src && alembic upgrade head
```

#### Run functional tests
```bash
docker-compose -f docker-compose-tests.yml up
```

#### Start on production
```bash
cp .env.example .env  # edit if necessary
docker-compose up
```

#### SuperUser
User with `superuser` rights is created via the CLI
```bash
python ./src/cli.py --email superuser@test.tt --password password
```