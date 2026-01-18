# GA4 Organic Traffic Analyzer

Aplicação Python para análise comparativa de tráfego orgânico utilizando a Google Analytics Data API (GA4). O sistema coleta, processa e gera relatórios detalhados comparando métricas entre dois períodos definidos.

## Visão Geral

Esta ferramenta foi desenvolvida para automatizar a análise de desempenho de tráfego orgânico em propriedades do Google Analytics 4. O sistema realiza coleta de dados via API oficial do Google, processa informações de múltiplas dimensões e gera relatórios comparativos em formato HTML e Excel.

## Características Principais

### Coleta de Dados

- **Autenticação OAuth 2.0**: Implementa fluxo completo de autenticação com o Google Cloud
- **Múltiplas Fontes Orgânicas**: Filtra dados de Google, Bing, DuckDuckGo, Yahoo e Yandex
- **Canal Organic Search**: Coleta separada de dados do canal padrão "Organic Search" do GA4
- **Análise por Dimensões**: Segmentação por dispositivo, fonte/meio e landing pages

### Métricas Coletadas

O sistema coleta as seguintes métricas para cada período:

- **Sessions**: Total de sessões iniciadas
- **Total Users**: Número total de usuários únicos
- **New Users**: Usuários que visitaram pela primeira vez
- **Engagement Rate**: Taxa de engajamento das sessões
- **Average Session Duration**: Duração média das sessões em segundos
- **Bounce Rate**: Taxa de rejeição
- **Conversions**: Total de conversões registradas
- **Total Revenue**: Receita total gerada

### Análise Comparativa

- Comparação automática entre dois períodos configuráveis
- Cálculo de variação percentual e absoluta para todas as métricas
- Análise de tendências e identificação de anomalias
- Segmentação por dispositivo (desktop, mobile, tablet)
- Análise detalhada de source/medium
- Ranking de landing pages por performance

### Sistema de Relatórios

#### Relatório HTML

Relatório interativo e responsivo contendo:

- **Resumo Executivo**: Métricas principais com indicadores visuais de variação
- **Análise Organic Search**: Seção dedicada ao canal Organic Search do GA4
- **Sistema de Alertas**: Classificação automática de performance (crítico, atenção, positivo)
- **Tabelas Comparativas**: Análise por dispositivo e fonte com variações percentuais
- **Top Landing Pages**: Ranking das páginas de entrada mais relevantes

#### Exportação Excel

Planilha estruturada em múltiplas abas:

- Resumo Comparativo: Visão consolidada com variações
- Por Dispositivo: Análise segmentada por tipo de dispositivo
- Por Fonte: Detalhamento de source/medium
- Dados Atuais: Dataset completo do período atual
- Dados Anteriores: Dataset completo do período anterior
- Landing Pages: Análise de páginas de entrada para ambos períodos

### Logging e Monitoramento

Sistema robusto de logging implementado com:

- **Registro em Arquivo**: Log persistente com timestamp e nível de severidade
- **Output Console**: Acompanhamento em tempo real da execução
- **Stack Trace**: Rastreamento completo de exceções para debugging
- **Métricas de Performance**: Registro de tempo de execução e volume de dados coletados

## Requisitos Técnicos

### Dependências Python

```
google-auth-oauthlib>=1.0.0
google-analytics-data>=0.17.0
pandas>=2.0.0
openpyxl>=3.1.0
```

### Requisitos de Ambiente

- Python 3.8 ou superior
- Credenciais OAuth 2.0 do Google Cloud Console
- Acesso de leitura à propriedade GA4 configurada

## Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/ga4-organic-analyzer.git
cd ga4-organic-analyzer
```

### 2. Configure Ambiente Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Instale Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure Credenciais

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Ative a Google Analytics Data API
4. Crie credenciais OAuth 2.0 para aplicação desktop
5. Baixe o arquivo JSON de credenciais
6. Renomeie para `client_secret.json` e coloque no diretório raiz

## Configuração

### Arquivo de Configuração

Edite a classe `Config` no início do script `main.py`:

```python
class Config:
    # ID da propriedade GA4 (encontrado em Admin > Property Settings)
    PROPERTY_ID = '272846783'
    
    # Arquivo de credenciais OAuth
    CLIENT_SECRET_FILE = 'client_secret.json'
    
    # Período atual de análise
    CURRENT_PERIOD_START = '2026-01-01'
    CURRENT_PERIOD_END = '2026-01-15'
    
    # Período de comparação
    PREVIOUS_PERIOD_START = '2025-01-01'
    PREVIOUS_PERIOD_END = '2025-01-15'
    
    # Fontes orgânicas a serem incluídas na análise
    ORGANIC_SOURCES = [
        'google / organic',
        'bing / organic',
        'duckduckgo / organic',
        'yahoo / organic',
        'yandex / organic'
    ]
```

### Personalização de Filtros

O sistema utiliza a API de filtros do GA4 para segmentação precisa:

**Filtro de Fontes Orgânicas**: Utiliza `sessionSourceMedium` com correspondência exata para cada fonte configurada

**Filtro Organic Search**: Utiliza `sessionDefaultChannelGroup` com correspondência exata para o canal padrão do GA4

## Execução

### Comando Básico

```bash
python main.py
```

### Primeira Execução

Na primeira execução, o navegador será aberto automaticamente para autorização OAuth:

1. Selecione a conta Google com acesso ao GA4
2. Conceda permissões de leitura ao Analytics
3. Aguarde confirmação de autorização
4. O script continuará automaticamente

### Execuções Subsequentes

As credenciais são armazenadas localmente. Execuções futuras não requerem nova autenticação, exceto se o token expirar.

## Estrutura de Saída

### Diretório de Relatórios

Todos os arquivos são salvos em `ga4_reports/`:

```
ga4_reports/
├── ga4_analyzer.log                           # Log de execução
├── ga4_organic_report_20260118_154230.html    # Relatório HTML
└── ga4_organic_report_20260118_154230.xlsx    # Planilha Excel
```

### Nomenclatura de Arquivos

Os arquivos são nomeados com timestamp no formato: `YYYYMMDD_HHMMSS`

Exemplo: `ga4_organic_report_20260118_154230.html`

## Arquitetura do Código

### Estrutura Modular

O código segue princípios de Clean Code com separação clara de responsabilidades:

#### Módulo de Configuração
- `Config`: Classe centralizada de configurações
- `setup_logging()`: Inicialização do sistema de logs

#### Módulo de Autenticação
- `authenticate_ga4()`: Gerenciamento de OAuth 2.0

#### Módulo de Coleta
- `create_organic_filter()`: Construção de filtros GA4
- `fetch_organic_traffic_data()`: Coleta de dados de fontes orgânicas
- `fetch_organic_search_data()`: Coleta específica do canal Organic Search
- `fetch_landing_pages()`: Coleta de landing pages

#### Módulo de Análise
- `calculate_comparison_metrics()`: Cálculo de variações entre períodos
- `analyze_by_dimension()`: Agregação por dimensões específicas

#### Módulo de Exportação
- `generate_html_report()`: Geração de relatório HTML
- `export_to_excel()`: Exportação para formato Excel

#### Orquestração
- `main()`: Função principal que coordena o fluxo de execução

### Type Hints

Todo o código utiliza type hints para melhor manutenibilidade:

```python
def fetch_organic_traffic_data(
    client: BetaAnalyticsDataClient,
    start_date: str,
    end_date: str,
    period_name: str
) -> Optional[pd.DataFrame]:
```

### Tratamento de Erros

Implementação robusta de try-catch em todas as operações críticas:

- Validação de arquivos de configuração
- Tratamento de falhas de autenticação
- Gerenciamento de respostas vazias da API
- Logging detalhado de exceções com stack trace

## Interpretação dos Resultados

### Indicadores de Variação

- **Positiva (Verde)**: Crescimento em relação ao período anterior
- **Negativa (Vermelho)**: Redução em relação ao período anterior

### Alertas de Performance

O sistema classifica automaticamente a performance de Organic Search:

- **Crítico**: Queda superior a 20% nas sessões
- **Atenção**: Qualquer queda percentual nas sessões
- **Positivo**: Crescimento em relação ao período anterior

### Métricas de Engajamento

- **Engagement Rate**: Valores mais altos indicam melhor qualidade de tráfego
- **Bounce Rate**: Valores mais baixos são preferíveis
- **Average Session Duration**: Maior tempo indica maior interesse no conteúdo

## Resolução de Problemas

### Erro de Autenticação

```
ERROR | authenticate_ga4 | Arquivo de credenciais não encontrado
```

**Solução**: Verifique se o arquivo `client_secret.json` está no diretório correto

### Propriedade GA4 Inválida

```
ERROR | fetch_organic_traffic_data | 400 Property not found
```

**Solução**: Confirme o PROPERTY_ID na classe Config

### Dados Vazios

```
WARNING | Nenhum dado de Organic Search encontrado
```

**Possíveis Causas**:
- Período selecionado não possui tráfego orgânico
- Filtros muito restritivos
- Propriedade GA4 recém-criada sem dados históricos

### Timeout de API

**Solução**: Reduza o intervalo de datas ou implemente paginação para grandes volumes

## Boas Práticas

### Frequência de Execução

- **Análise Semanal**: Comparação semana a semana
- **Análise Mensal**: Comparação mês a mês
- **Análise de Campanhas**: Antes/depois de ações de marketing

### Segurança

- Nunca faça commit do arquivo `client_secret.json`
- Adicione ao `.gitignore`:
  ```
  client_secret.json
  token.json
  ga4_reports/
  .venv/
  ```

### Performance

Para propriedades com alto volume de tráfego:
- Considere implementar cache de resultados
- Utilize paginação na API para datasets grandes
- Execute análises em horários de baixo uso

## Limitações Conhecidas

- **Quota da API**: Limite de 10.000 requisições por dia (quota padrão do Google)
- **Tamanho de Resposta**: Limite de 100.000 linhas por requisição
- **Sampling**: Pode ocorrer em propriedades com altíssimo volume

## Contribuindo

Contribuições são bem-vindas. Para mudanças significativas:

1. Abra uma issue descrevendo a proposta
2. Faça fork do repositório
3. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
4. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
5. Push para a branch (`git push origin feature/NovaFuncionalidade`)
6. Abra um Pull Request

## Roadmap

Funcionalidades planejadas:

- [ ] Interface web com Streamlit/Dash
- [ ] Agendamento automático de execuções
- [ ] Notificações por email de alertas críticos
- [ ] Integração com Data Studio/Looker
- [ ] Exportação para formatos adicionais (PDF, CSV)
- [ ] Análise de palavras-chave (integração Search Console)
- [ ] Comparação com múltiplos períodos históricos
- [ ] Machine Learning para previsão de tendências

## Licença

MIT License - veja o arquivo LICENSE para detalhes

## Suporte

Para reportar bugs ou solicitar funcionalidades, abra uma issue no repositório.

## Autores

Analytics Team - Versão 2.0

## Changelog

### v2.0.0 (2026-01-18)
- Implementação de análise comparativa entre períodos
- Adição de seção específica para Organic Search
- Sistema de logging robusto
- Relatórios HTML responsivos
- Exportação Excel multi-abas

### v1.0.0 (2025-12-01)
- Versão inicial com coleta básica de dados GA4
