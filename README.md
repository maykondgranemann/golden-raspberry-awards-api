# 🎮 Golden Raspberry Awards API

API RESTful para processar e analisar os vencedores do prêmio **Golden Raspberry Awards**, seguindo os princípios de **Clean Architecture** e boas práticas de desenvolvimento.

📌 **Projeto Público no GitHub:**  
🔗 [Golden Raspberry Awards API - Projeto Kanban](https://github.com/users/maykondgranemann/projects/7)  

Este projeto foi desenvolvido de forma **estruturada e incremental**, utilizando **Kanban**, **Pull Requests bem documentados** e **Integração Contínua (CI/CD)** para garantir qualidade e rastreabilidade.

---

## 🚀 **Tecnologias Utilizadas**
- **Linguagem:** Python 3.13.1
- **Framework:** FastAPI
- **Banco de Dados:** SQLite
- **Manipulação de Dados:** Pandas
- **Tarefas Assíncronas:** Celery (backend em memória)
- **Cache:** `functools.lru_cache` , caso fosse possivel instalar seria Redis
- **Infraestrutura:** Docker, Kubernetes e Terraform
- **CI/CD:** GitHub Actions
- **Gerenciamento de Dependências:** Poetry
- **Variáveis de Ambiente:** python-dotenv

---

## 📂 **Estrutura do Repositório**
```
📂 golden-raspberry-awards-api/
├── 📂 app/                     # Código-fonte principal
│   ├── 📂 api/                 # Rotas do FastAPI
│   ├── 📂 models/              # Definição de tabelas SQLAlchemy
│   ├── 📂 services/            # Regras de negócio
│   ├── 📂 repositories/        # Acesso ao banco de dados
│   ├── 📂 db/                  # Configuração do banco SQLite
│   ├── 📂 tasks/               # Celery para importação do CSV
│   ├── 📂 utils/               # Funções auxiliares (ex: cache)
│   ├── main.py                 # Ponto de entrada do FastAPI
│   ├── config.py               # Configuração de variáveis de ambiente
├── 📂 tests/                   # Testes automatizados com pytest
│   ├── test_api.py             # Testes de integração
│   ├── test_services.py        # Testes de lógica
│   ├── test_db.py              # Testes do banco de dados
├── 📂 infrastructure/          # Configuração de Infraestrutura
│   ├── Dockerfile              # Container da API
│   ├── docker-compose.yml      # Configuração do ambiente com Docker
│   ├── deployment.yaml         # Manifesto Kubernetes
│   ├── main.tf                 # Script Terraform para deploy no GCP
├── 📂 data/                    # Arquivos CSV de entrada (para testes)
│   ├── movielist.csv           # Dataset original
├── 📂 .github/                 # Workflows de CI/CD
│   ├── workflows/
│       ├── ci.yml              # CI/CD básico
├── .gitignore                  # Arquivos ignorados no Git
├── pyproject.toml              # Gerenciamento de dependências com Poetry
├── README.md                   # Documentação do projeto
├── LICENSE                     # Licença do projeto (MIT)
```

---

## 🌳 **Estrutura de Branches**
O desenvolvimento segue a abordagem de **Git Flow**, com a seguinte estrutura:

🔹 **Branches Principais**  
- `main` → Versão estável e pronta para produção 🚀  
- `homolog` → Testes antes de liberar para produção 🔍  
- `develop` → Desenvolvimento contínuo 🛠️  

🔹 **Branches de Features**  
Cada nova funcionalidade ou melhoria é implementada em uma **branch específica** baseada em `develop`. Exemplo:  
- `feature/import-csv`
- `feature/create-endpoint`
- `feature/add-ci-cd`
- `feature/setup-github`

---

## 🔄 **Processo de Desenvolvimento**
O projeto segue um **workflow estruturado** para manter o código organizado e rastreável:

1️⃣ **Criamos uma Issue no GitHub** baseada nas tarefas do [Projeto Kanban](https://github.com/users/maykondgranemann/projects/7)  
2️⃣ **Criado uma nova branch baseada em `develop`**  
3️⃣ **Desenvolvido a feature e realizado commits bem documentados**  
4️⃣ **Aberto um Pull Request (`feature/xyz` → `develop`)** para revisão  
5️⃣ **A Integração Contínua (CI/CD) é acionada automaticamente** no GitHub Actions  
6️⃣ **Após aprovação, feito merge de `develop` → `homolog`**  
7️⃣ **Se tudo estiver validado, feito merge de `homolog` → `main`**  

🔗 **Veja todos os Pull Requests criados no projeto:**  
[📌 GitHub PRs - Abertos e Fechados](https://github.com/maykondgranemann/golden-raspberry-awards-api/pulls)

---

## 🛠️ **Como Rodar o Projeto**
### 🔧 Rodando Localmente
```bash
git clone https://github.com/maykondgranemann/golden-raspberry-awards-api.git
cd golden-raspberry-awards-api
poetry install
uvicorn app.main:app --reload
```

### 🐥 Rodando com Docker
```bash
docker-compose up --build
```

### ✅ Rodando Testes
```bash
pytest
```


