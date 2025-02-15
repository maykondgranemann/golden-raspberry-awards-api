# 🎬 Golden Raspberry Awards API

API RESTful para processar e analisar os vencedores do prêmio **Golden Raspberry Awards**, seguindo os princípios de **Clean Architecture** e boas práticas de desenvolvimento.

📌 **Projeto Público no GitHub:**  
🔗 [Golden Raspberry Awards API - Projeto Kanban](https://github.com/users/maykondgranemann/projects/7)  

Este projeto foi desenvolvido de forma **estruturada e incremental**, utilizando **Kanban**, **Pull Requests bem documentados** e **Integração Contínua (CI/CD)** via GitHub Actions, sendo **implantado diretamente no Kubernetes no Google Cloud Platform (GCP)** e disponível publicamente.

---

## 🚀 **Tecnologias Utilizadas**
- **Linguagem:** Python 3.13.1
- **Framework:** FastAPI
- **Banco de Dados:** SQLite
- **Manipulação de Dados:** Pandas
- **Tarefas Assíncronas:** Celery (backend em memória)
- **Cache:** `functools.lru_cache` , caso fosse possivel instalar seria Redis
- **Infraestrutura:** Docker, Kubernetes, Terraform e GCP
- **CI/CD:** GitHub Actions
- **Gerenciamento de Dependências:** Poetry
- **Variáveis de Ambiente:** python-dotenv

---

## 🌎 **Infraestrutura e Deploy**
Este projeto utiliza **Infraestrutura como Código (IaC)** para garantir **automação total do deploy**, incluindo:

✅ **GitHub Actions:** CI/CD automatizado para testes, build e deploy  
✅ **Docker Hub:** Imagem disponível publicamente em [Docker Hub](https://hub.docker.com/r/zuplae/golden-raspberry-awards-api)  
✅ **Terraform:** Provisiona os recursos no Google Cloud Platform (GCP)  
✅ **Kubernetes (GKE):** Orquestração da aplicação no Google Kubernetes Engine (GKE)  
✅ **Google Cloud Platform (GCP):** Hospedagem da API no cluster Kubernetes  

---

## 📡 **Acesso à API**
A API está disponível publicamente no GCP e pode ser acessada em:

🔗 **Base URL:** [http://107.178.211.239/](http://107.178.211.239/)  

### 📌 **Endpoints Disponíveis**
- **`/health`** → Verifica se a API está rodando corretamente  
- **`/docs`** → Documentação interativa gerada pelo FastAPI  

```bash
curl http://107.178.211.239/health

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

1️⃣ **Criado uma Issue no GitHub** baseada nas tarefas do [Projeto Kanban](https://github.com/users/maykondgranemann/projects/7)  
2️⃣ **Criado uma nova branch baseada em `develop`**  
3️⃣ **Desenvolvido a feature e realizado commits bem documentados**  
4️⃣ **Aberto um Pull Request (`feature/xyz` → `develop`)** para revisão  
5️⃣ **A Integração Contínua (CI/CD) é acionada automaticamente** no GitHub Actions  
6️⃣ **Após aprovação, feito merge de `develop` → `homolog`**  
7️⃣ **Se tudo estiver validado, feito merge de `homolog` → `main`**  

🔗 **Veja todos os Pull Requests criados no projeto:**  
[📌 GitHub PRs - Fechados](https://github.com/maykondgranemann/golden-raspberry-awards-api/pulls?q=is%3Apr+is%3Aclosed)

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
pytest tests
```
---

## 📜 Licença
### Este projeto está sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

---

## 📬 Contato
### Caso tenha dúvidas ou sugestões, sinta-se à vontade para entrar em contato:

- 📧 Email: maykondgranemann@gmail.com
- 🔗 LinkedIn: [Maykon Dyego Granemann](https://www.linkedin.com/in/maykongranemann/)
- 🚀 GitHub: [maykondgranemann](https://github.com/maykondgranemann)
- 💬 **WhatsApp:** [Fale comigo no WhatsApp](https://wa.me/5547997080273) 
