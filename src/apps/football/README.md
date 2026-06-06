# Módulo Django Football - Integração & Sincronização

Este módulo é responsável pela integração com a API externa de futebol (API-Football) para obter dados atualizados de seleções, elencos, partidas, fases e estatísticas em tempo real, servindo tudo através de uma API REST desenvolvida em Django REST Framework (DRF).

---

## 🔑 1. Como Obter a Chave da API

A API-Football possui duas formas de contratação/autenticação. Escolha **uma** delas:

### Opção A: Via RapidAPI (Recomendado & Prático)
1. Acesse o portal da [RapidAPI - API-Football](https://rapidapi.com/api-sports/api/api-football).
2. Se ainda não possui conta, crie uma (gratuita).
3. Vá para a aba **Pricing** (Preços).
4. Selecione o plano **Basic / Free** (100 requisições diárias gratuitas) e clique em **Subscribe**.
5. No painel de testes do RapidAPI, localize o campo `x-rapidapi-key`. Este é o seu token.

### Opção B: Direto na API-Sports (Site Oficial)
1. Acesse o site oficial do [API-Sports Dashboard](https://dashboard.api-sports.io/).
2. Faça o cadastro e ative sua conta.
3. No painel, crie uma chave de acesso (API Key).

---

## ⚙️ 2. Configuração do `.env`

Crie um arquivo `.env` na raiz do projeto (`/home/jader/Projects/bengalafc-api/.env`) com base nas configurações da opção escolhida acima:

### Se você escolheu a RapidAPI (Opção A):
```env
FOOTBALL_API_URL=https://api-football-v1.p.rapidapi.com
FOOTBALL_API_HEADER=x-rapidapi-key
FOOTBALL_API_KEY=sua_chave_da_rapidapi_aqui

# Configuração padrão de campeonato (Copa do Mundo 2022)
FOOTBALL_API_DEFAULT_COMPETITION_ID=1
FOOTBALL_API_DEFAULT_SEASON=2022
```

### Se você escolheu a API-Sports Direto (Opção B):
```env
FOOTBALL_API_URL=https://v3.football.api-sports.io
FOOTBALL_API_HEADER=x-apisports-key
FOOTBALL_API_KEY=sua_chave_da_apisports_aqui

# Configuração padrão de campeonato (Copa do Mundo 2022)
FOOTBALL_API_DEFAULT_COMPETITION_ID=1
FOOTBALL_API_DEFAULT_SEASON=2022
```

---

## 🚀 3. Primeiros Passos

### Instalar dependências e rodar migrações
Certifique-se de que o seu ambiente virtual esteja ativo e rode os comandos na raiz do projeto:

```bash
# Rodar migrações para criar as tabelas no banco de dados
.venv/bin/python src/manage.py migrate
```

---

## 🔄 4. Como Sincronizar o Banco de Dados

### Sincronização Completa (Recomendado)
Você pode rodar toda a cadeia de importação na ordem lógica de chaves estrangeiras com um único comando:

```bash
# Sincronizar Copa do Mundo 2022
.venv/bin/python src/manage.py sync_all --competition-id 1 --season 2022
```

### Sincronização Individual (Passo a Passo)
Caso queira executar individualmente cada serviço de sincronização:

```bash
# 1. Seleções/Equipes
.venv/bin/python src/manage.py sync_teams --league 1 --season 2022

# 2. Jogadores
.venv/bin/python src/manage.py sync_players --season 2022

# 3. Competição
.venv/bin/python src/manage.py sync_competitions --competition-id 1 --season 2022

# 4. Fases da competição
.venv/bin/python src/manage.py sync_stages --competition-id 1 --season 2022

# 5. Calendário de Partidas
.venv/bin/python src/manage.py sync_fixtures --competition-id 1 --season 2022

# 6. Estatísticas (equipes e jogadores)
.venv/bin/python src/manage.py sync_statistics --competition-id 1
```

*Nota: Se os comandos forem executados sem chave de API ativa, os serviços utilizarão automaticamente dados de salvaguarda (mock/fallbacks) para garantir o funcionamento local.*

---

## 📡 5. Endpoints da API REST (Consumo dos Dados)

Inicie o servidor de desenvolvimento:
```bash
.venv/bin/python src/manage.py runserver
```

Acesse no navegador os seguintes endpoints:

* **Listar Equipes:** `http://127.0.0.1:8000/api/teams/`
  * *Exemplo de Filtro:* `?country=Brazil`
* **Listar Jogadores:** `http://127.0.0.1:8000/api/players/`
  * *Exemplo de Filtro:* `?nationality=Brazil` ou `?team_external_id=6` (Brasil na API-Football) ou `?team=5` (ID local do Brasil no seu banco)
* **Listar Partidas (Fixtures):** `http://127.0.0.1:8000/api/fixtures/`
  * *Exemplo de Filtro:* `?status=FT` (Partidas Finalizadas)
* **Adicionar Campeonato (POST):** Envie um POST para `http://127.0.0.1:8000/api/competitions/` (necessário estar autenticado).

---

## 🧪 6. Como Rodar os Testes

Para validar a integridade lógica e os endpoints da API:
```bash
.venv/bin/python src/manage.py test apps.football
```
