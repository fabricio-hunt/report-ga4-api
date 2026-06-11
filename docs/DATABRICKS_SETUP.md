# Setup Databricks — GA4 Report Collector

Este guia descreve como executar o projeto via **Databricks Repos** e **Jobs**, com saída exclusiva em **Excel externo** (sem tabelas Delta ou persistência no catálogo).

## 1. Conectar o repositório Git

1. No workspace Databricks, abra **Repos** → **Add Repo**.
2. Informe a URL do repositório Git e selecione a branch de trabalho.
3. Após o clone, o código ficará em `/Repos/<usuario>/Report-GA4-DataBricks`.

## 2. Criar Volume para arquivos Excel (opcional, recomendado)

O Volume UC é armazenamento de **arquivos**, não tabelas. Use-o como pasta compartilhada para os `.xlsx`.

```sql
CREATE VOLUME IF NOT EXISTS <catalog>.<schema>.ga4_reports;
```

Atualize `config/default.yaml` ou defina a variável de ambiente:

```
GA4_OUTPUT_DIR=/Volumes/<catalog>/<schema>/ga4_reports
```

Alternativa: mount externo (ADLS/S3) em `/mnt/ga4-reports`.

## 3. Configurar Secrets OAuth

### 3.1 Gerar refresh token localmente

1. Na máquina local, execute uma coleta com sucesso:
   ```powershell
   pip install -r requirements.txt
   python jobs/run_main.py
   ```
2. Extraia o refresh token:
   ```powershell
   python tools/extract_refresh_token.py
   ```

### 3.2 Criar Secret Scope no Databricks

Via CLI Databricks ou UI (**Settings → Secrets**):

```bash
databricks secrets create-scope ga4-oauth
```

Registre os secrets:

| Key | Valor |
|-----|-------|
| `client_secret_json` | Conteúdo completo do `client_secret.json` |
| `refresh_token` | Token obtido via `tools/extract_refresh_token.py` |

## 4. Criar Jobs

Recomenda-se cluster **single-node** (runtime 14.x+, Python 3.10+). Não é necessário Spark distribuído.

### Job principal (mensal)

| Campo | Valor |
|-------|-------|
| Tipo | Python script ou Notebook |
| Path | `/Repos/<user>/Report-GA4-DataBricks/jobs/run_main.py` |
| Ou notebook | `/Repos/<user>/Report-GA4-DataBricks/notebooks/00_run_main.py` |

**Variáveis de ambiente do Job:**

```
GA4_ENV=databricks
GA4_OUTPUT_DIR=/Volumes/<catalog>/<schema>/ga4_reports
GA4_ANALYSIS_START=2026-05-01
GA4_ANALYSIS_END=2026-05-31
```

**Parâmetros CLI (alternativa):**

```
--analysis-start 2026-05-01 --analysis-end 2026-05-31
```

### Jobs auxiliares (sob demanda)

| Job | Script |
|-----|--------|
| Farma Web Orgânico | `jobs/run_bemol_app.py` |
| Farma Web Total YoY | `jobs/run_farma_comparacao.py` |

## 5. Dependências no cluster

**Opção A — Notebook wrapper (recomendada para Repos):**

O notebook [`notebooks/00_run_main.py`](notebooks/00_run_main.py) executa `%pip install -r ../requirements.txt` antes do job.

**Opção B — Bibliotecas no cluster:**

Instale no cluster via PyPI:

- `google-analytics-data`
- `google-auth-oauthlib`
- `google-auth`
- `pandas`
- `openpyxl`
- `pyyaml`

## 6. Execução local (testes)

```powershell
$env:GA4_ENV = "local"
$env:GA4_ANALYSIS_START = "2026-05-01"
$env:GA4_ANALYSIS_END = "2026-05-31"
python jobs/run_main.py
```

Por padrão, os arquivos Excel são gravados em:

```
C:\Users\fabricio.barauna\OneDrive - BEMOL S A\Documentos
```

Override via `$env:GA4_OUTPUT_DIR = "C:\caminho\customizado"`.

## 7. Validar configuração

```powershell
python validate_config.py
```

## 8. Estrutura do projeto

```
src/           → lógica reutilizável (auth, collectors, export)
jobs/          → entrypoints para Jobs Databricks
config/        → defaults não-sensíveis (YAML)
notebooks/     → wrapper opcional para Repos
tools/         → utilitários (extract_refresh_token)
```

## 9. Troubleshooting

| Problema | Solução |
|----------|---------|
| `Erro na autenticação` no Job | Verificar secrets `client_secret_json` e `refresh_token` |
| Refresh token inválido | Reautenticar localmente e atualizar secret |
| Permissão negada no Volume | Conceder `READ FILES`, `WRITE FILES` no Volume UC |
| Pacote não encontrado | Executar `%pip install -r requirements.txt` ou instalar no cluster |
| Path placeholder no output | Substituir `<catalog>/<schema>/<volume>` em `GA4_OUTPUT_DIR` |

## 10. O que não fazer

- Não commitar `client_secret.json` nem `token.pickle`
- Não gravar saída em paths relativos dentro do Repo (read-only em runtime)
- Não usar Delta/Parquet se o requisito é apenas Excel externo para stakeholders
