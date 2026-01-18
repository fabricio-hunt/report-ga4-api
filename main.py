"""
GA4 Organic Traffic Analyzer
Análise comparativa de tráfego orgânico entre dois períodos
Author: Analytics Team
Version: 2.0
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, 
    OrderBy, FilterExpression, Filter
)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configurações centralizadas da aplicação"""
    PROPERTY_ID = '272846783'
    CLIENT_SECRET_FILE = 'client_secret.json'
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    
    # Períodos de análise
    CURRENT_PERIOD_START = '2026-01-01'
    CURRENT_PERIOD_END = '2026-01-15'
    PREVIOUS_PERIOD_START = '2025-01-01'
    PREVIOUS_PERIOD_END = '2025-01-15'
    
    # Filtros de tráfego orgânico
    ORGANIC_SOURCES = [
        'google / organic',
        'bing / organic',
        'duckduckgo / organic',
        'yahoo / organic',
        'yandex / organic'
    ]
    
    # Output
    OUTPUT_DIR = 'ga4_reports'
    LOG_FILE = 'ga4_analyzer.log'

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging() -> logging.Logger:
    """
    Configura o sistema de logging com arquivo e console
    
    Returns:
        Logger configurado
    """
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(Config.OUTPUT_DIR, Config.LOG_FILE)
    
    # Configurar formato
    log_format = '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar handlers
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("GA4 Organic Traffic Analyzer iniciado")
    logger.info("="*80)
    
    return logger

logger = setup_logging()

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def authenticate_ga4() -> Optional[BetaAnalyticsDataClient]:
    """
    Autentica no Google Analytics 4 usando OAuth 2.0
    
    Returns:
        Cliente autenticado do GA4 ou None em caso de erro
    """
    try:
        logger.info(f"Iniciando autenticação com {Config.CLIENT_SECRET_FILE}")
        
        if not os.path.exists(Config.CLIENT_SECRET_FILE):
            logger.error(f"Arquivo de credenciais não encontrado: {Config.CLIENT_SECRET_FILE}")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(
            Config.CLIENT_SECRET_FILE, 
            Config.SCOPES
        )
        
        credentials = flow.run_local_server(port=0)
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        logger.info("✓ Autenticação concluída com sucesso")
        return client
        
    except Exception as e:
        logger.error(f"Erro na autenticação: {str(e)}", exc_info=True)
        return None

# ============================================================================
# FILTROS E QUERIES
# ============================================================================

def create_organic_filter() -> FilterExpression:
    """
    Cria filtro para tráfego orgânico baseado em source/medium
    
    Returns:
        FilterExpression configurado para fontes orgânicas
    """
    # Criar filtro OR para múltiplas fontes orgânicas
    filter_expressions = []
    
    for source_medium in Config.ORGANIC_SOURCES:
        filter_expressions.append(
            FilterExpression(
                filter=Filter(
                    field_name='sessionSourceMedium',
                    string_filter=Filter.StringFilter(
                        match_type=Filter.StringFilter.MatchType.EXACT,
                        value=source_medium
                    )
                )
            )
        )
    
    # Combinar com OR - sintaxe correta
    organic_filter = FilterExpression(
        or_group={'expressions': filter_expressions}
    )
    
    logger.info(f"Filtro orgânico criado com {len(Config.ORGANIC_SOURCES)} fontes")
    return organic_filter

# ============================================================================
# COLETA DE DADOS
# ============================================================================

def fetch_organic_search_data(
    client: BetaAnalyticsDataClient,
    start_date: str,
    end_date: str,
    period_name: str
) -> Optional[pd.DataFrame]:
    """
    Coleta dados específicos do canal 'Organic Search'
    
    Args:
        client: Cliente autenticado do GA4
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
        period_name: Nome do período para logging
        
    Returns:
        DataFrame com os dados ou None em caso de erro
    """
    try:
        logger.info(f"Coletando dados de Organic Search: {period_name} ({start_date} a {end_date})")
        
        request = RunReportRequest(
            property=f"properties/{Config.PROPERTY_ID}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionDefaultChannelGroup")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="engagementRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="conversions"),
                Metric(name="totalRevenue")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name='sessionDefaultChannelGroup',
                    string_filter=Filter.StringFilter(
                        match_type=Filter.StringFilter.MatchType.EXACT,
                        value='Organic Search'
                    )
                )
            ),
            order_bys=[OrderBy(dimension={'dimension_name': 'date'})]
        )
        
        response = client.run_report(request=request)
        
        # Processar resposta
        data = []
        for row in response.rows:
            data.append({
                'date': row.dimension_values[0].value,
                'channel': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'new_users': int(row.metric_values[2].value),
                'engagement_rate': float(row.metric_values[3].value),
                'avg_session_duration': float(row.metric_values[4].value),
                'bounce_rate': float(row.metric_values[5].value),
                'conversions': float(row.metric_values[6].value),
                'revenue': float(row.metric_values[7].value)
            })
        
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning(f"Nenhum dado de Organic Search encontrado para o período {period_name}")
            return df
        
        # Adicionar coluna de período
        df['period'] = period_name
        
        logger.info(f"✓ Coletados {len(df)} registros de Organic Search para {period_name}")
        logger.info(f"  Total de sessões: {df['sessions'].sum():,}")
        logger.info(f"  Total de usuários: {df['users'].sum():,}")
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao coletar dados de Organic Search do período {period_name}: {str(e)}", exc_info=True)
        return None

def fetch_organic_traffic_data(
    client: BetaAnalyticsDataClient,
    start_date: str,
    end_date: str,
    period_name: str
) -> Optional[pd.DataFrame]:
    """
    Coleta dados de tráfego orgânico para um período específico
    
    Args:
        client: Cliente autenticado do GA4
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
        period_name: Nome do período para logging
        
    Returns:
        DataFrame com os dados ou None em caso de erro
    """
    try:
        logger.info(f"Coletando dados do período: {period_name} ({start_date} a {end_date})")
        
        request = RunReportRequest(
            property=f"properties/{Config.PROPERTY_ID}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSourceMedium"),
                Dimension(name="deviceCategory")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="engagementRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="conversions"),
                Metric(name="totalRevenue")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=create_organic_filter(),
            order_bys=[OrderBy(dimension={'dimension_name': 'date'})]
        )
        
        response = client.run_report(request=request)
        
        # Processar resposta
        data = []
        for row in response.rows:
            data.append({
                'date': row.dimension_values[0].value,
                'source_medium': row.dimension_values[1].value,
                'device': row.dimension_values[2].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'new_users': int(row.metric_values[2].value),
                'engagement_rate': float(row.metric_values[3].value),
                'avg_session_duration': float(row.metric_values[4].value),
                'bounce_rate': float(row.metric_values[5].value),
                'conversions': float(row.metric_values[6].value),
                'revenue': float(row.metric_values[7].value)
            })
        
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning(f"Nenhum dado encontrado para o período {period_name}")
            return df
        
        # Adicionar coluna de período
        df['period'] = period_name
        
        logger.info(f"✓ Coletados {len(df)} registros para {period_name}")
        logger.info(f"  Total de sessões: {df['sessions'].sum():,}")
        logger.info(f"  Total de usuários: {df['users'].sum():,}")
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao coletar dados do período {period_name}: {str(e)}", exc_info=True)
        return None

def fetch_landing_pages(
    client: BetaAnalyticsDataClient,
    start_date: str,
    end_date: str,
    period_name: str
) -> Optional[pd.DataFrame]:
    """
    Coleta landing pages do tráfego orgânico
    
    Args:
        client: Cliente autenticado do GA4
        start_date: Data inicial
        end_date: Data final
        period_name: Nome do período
        
    Returns:
        DataFrame com landing pages ou None
    """
    try:
        logger.info(f"Coletando landing pages do período: {period_name}")
        
        request = RunReportRequest(
            property=f"properties/{Config.PROPERTY_ID}",
            dimensions=[
                Dimension(name="landingPage")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="bounceRate")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=create_organic_filter(),
            order_bys=[OrderBy(metric={'metric_name': 'sessions'}, desc=True)],
            limit=20
        )
        
        response = client.run_report(request=request)
        
        data = []
        for row in response.rows:
            data.append({
                'landing_page': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'bounce_rate': float(row.metric_values[2].value),
                'period': period_name
            })
        
        df = pd.DataFrame(data)
        logger.info(f"✓ Coletadas {len(df)} landing pages para {period_name}")
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao coletar landing pages: {str(e)}", exc_info=True)
        return None

# ============================================================================
# ANÁLISE E COMPARAÇÃO
# ============================================================================

def calculate_comparison_metrics(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame
) -> Dict:
    """
    Calcula métricas comparativas entre dois períodos
    
    Args:
        df_current: Dados do período atual
        df_previous: Dados do período anterior
        
    Returns:
        Dicionário com métricas comparativas
    """
    logger.info("Calculando métricas comparativas")
    
    metrics = {}
    
    # Agregar totais
    current_totals = {
        'sessions': df_current['sessions'].sum(),
        'users': df_current['users'].sum(),
        'new_users': df_current['new_users'].sum(),
        'conversions': df_current['conversions'].sum(),
        'revenue': df_current['revenue'].sum(),
        'engagement_rate': df_current['engagement_rate'].mean(),
        'bounce_rate': df_current['bounce_rate'].mean(),
        'avg_session_duration': df_current['avg_session_duration'].mean()
    }
    
    previous_totals = {
        'sessions': df_previous['sessions'].sum(),
        'users': df_previous['users'].sum(),
        'new_users': df_previous['new_users'].sum(),
        'conversions': df_previous['conversions'].sum(),
        'revenue': df_previous['revenue'].sum(),
        'engagement_rate': df_previous['engagement_rate'].mean(),
        'bounce_rate': df_previous['bounce_rate'].mean(),
        'avg_session_duration': df_previous['avg_session_duration'].mean()
    }
    
    # Calcular variações
    for key in current_totals.keys():
        current_val = current_totals[key]
        previous_val = previous_totals[key]
        
        if previous_val > 0:
            variation = ((current_val - previous_val) / previous_val) * 100
        else:
            variation = 0 if current_val == 0 else 100
        
        metrics[key] = {
            'current': current_val,
            'previous': previous_val,
            'variation': variation,
            'variation_abs': current_val - previous_val
        }
    
    logger.info("✓ Métricas comparativas calculadas")
    return metrics

def analyze_by_dimension(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
    dimension: str
) -> pd.DataFrame:
    """
    Analisa dados agregados por dimensão específica
    
    Args:
        df_current: Dados do período atual
        df_previous: Dados do período anterior
        dimension: Dimensão para agregação (source_medium, device, etc)
        
    Returns:
        DataFrame com análise comparativa por dimensão
    """
    logger.info(f"Analisando por dimensão: {dimension}")
    
    # Agregar período atual
    current_agg = df_current.groupby(dimension).agg({
        'sessions': 'sum',
        'users': 'sum',
        'revenue': 'sum'
    }).add_suffix('_current')
    
    # Agregar período anterior
    previous_agg = df_previous.groupby(dimension).agg({
        'sessions': 'sum',
        'users': 'sum',
        'revenue': 'sum'
    }).add_suffix('_previous')
    
    # Combinar
    comparison = current_agg.join(previous_agg, how='outer').fillna(0)
    
    # Calcular variações
    comparison['sessions_var_%'] = (
        (comparison['sessions_current'] - comparison['sessions_previous']) / 
        comparison['sessions_previous'].replace(0, 1) * 100
    )
    
    comparison['users_var_%'] = (
        (comparison['users_current'] - comparison['users_previous']) / 
        comparison['users_previous'].replace(0, 1) * 100
    )
    
    comparison['revenue_var_%'] = (
        (comparison['revenue_current'] - comparison['revenue_previous']) / 
        comparison['revenue_previous'].replace(0, 1) * 100
    )
    
    # Ordenar por sessões atuais
    comparison = comparison.sort_values('sessions_current', ascending=False)
    
    return comparison

# ============================================================================
# GERAÇÃO DE RELATÓRIO HTML
# ============================================================================

def generate_html_report(
    metrics: Dict,
    organic_search_metrics: Dict,
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
    comparison_device: pd.DataFrame,
    comparison_source: pd.DataFrame,
    landing_current: pd.DataFrame,
    landing_previous: pd.DataFrame
) -> str:
    """
    Gera relatório HTML completo com análise comparativa
    
    Args:
        metrics: Métricas comparativas gerais
        organic_search_metrics: Métricas específicas de Organic Search
        df_current: Dados período atual
        df_previous: Dados período anterior
        comparison_device: Comparação por dispositivo
        comparison_source: Comparação por fonte
        landing_current: Landing pages atuais
        landing_previous: Landing pages anteriores
        
    Returns:
        String com HTML completo
    """
    logger.info("Gerando relatório HTML")
    
    # Função auxiliar para formatar variação
    def format_variation(value: float) -> str:
        color = 'green' if value >= 0 else 'red'
        icon = '▲' if value >= 0 else '▼'
        return f'<span style="color: {color}; font-weight: bold;">{icon} {value:+.2f}%</span>'
    
    # Função auxiliar para formatar números
    def format_number(value: float, decimals: int = 0) -> str:
        if decimals == 0:
            return f"{int(value):,}".replace(',', '.')
        return f"{value:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Início do HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Tráfego Orgânico - GA4</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f7fa;
                color: #2d3748;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .period-info {{
                background: #edf2f7;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            
            .period-box {{
                background: white;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }}
            
            .period-box h3 {{
                color: #667eea;
                margin-bottom: 5px;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .metric-card {{
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 25px;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            
            .metric-label {{
                color: #718096;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
            }}
            
            .metric-value {{
                font-size: 2.2em;
                font-weight: bold;
                color: #2d3748;
                margin-bottom: 10px;
            }}
            
            .metric-comparison {{
                font-size: 0.9em;
                color: #718096;
            }}
            
            .section {{
                margin-bottom: 50px;
            }}
            
            .section-title {{
                font-size: 1.8em;
                color: #2d3748;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
            }}
            
            th {{
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            tr:hover {{
                background: #f7fafc;
            }}
            
            .alert {{
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            
            .alert-success {{
                background: #d4edda;
                border-left: 4px solid #28a745;
                color: #155724;
            }}
            
            .alert-warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                color: #856404;
            }}
            
            .alert-danger {{
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }}
            
            footer {{
                background: #2d3748;
                color: white;
                text-align: center;
                padding: 20px;
                margin-top: 40px;
            }}
            
            .highlight {{
                background: #fef3c7;
                padding: 2px 6px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Relatório de Tráfego Orgânico</h1>
                <p>Análise Comparativa - Google Analytics 4</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </header>
            
            <div class="content">
                <!-- Informações dos Períodos -->
                <div class="period-info">
                    <div class="period-box">
                        <h3>📅 Período Anterior</h3>
                        <p><strong>{Config.PREVIOUS_PERIOD_START}</strong> até <strong>{Config.PREVIOUS_PERIOD_END}</strong></p>
                    </div>
                    <div class="period-box">
                        <h3>📅 Período Atual</h3>
                        <p><strong>{Config.CURRENT_PERIOD_START}</strong> até <strong>{Config.CURRENT_PERIOD_END}</strong></p>
                    </div>
                </div>
    """
    
    # Métricas Principais
    html += """
                <div class="section">
                    <h2 class="section-title">📈 Métricas Principais</h2>
                    <div class="metrics-grid">
    """
    
    metric_configs = [
        ('sessions', 'Sessões', '🔍', 0),
        ('users', 'Usuários', '👥', 0),
        ('new_users', 'Novos Usuários', '✨', 0),
        ('conversions', 'Conversões', '🎯', 1),
        ('revenue', 'Receita (R$)', '💰', 2),
        ('engagement_rate', 'Taxa de Engajamento', '❤️', 2),
        ('bounce_rate', 'Taxa de Rejeição', '↩️', 2),
        ('avg_session_duration', 'Duração Média (seg)', '⏱️', 0)
    ]
    
    for metric_key, label, icon, decimals in metric_configs:
        m = metrics[metric_key]
        html += f"""
                        <div class="metric-card">
                            <div class="metric-label">{icon} {label}</div>
                            <div class="metric-value">{format_number(m['current'], decimals)}</div>
                            <div class="metric-comparison">
                                {format_variation(m['variation'])} vs período anterior
                                <br><small>Anterior: {format_number(m['previous'], decimals)}</small>
                            </div>
                        </div>
        """
    
    html += """
                    </div>
                </div>
                
                <!-- Métricas Organic Search -->
                <div class="section">
                    <h2 class="section-title">🌿 Organic Search</h2>
                    <div class="metrics-grid">
    """
    
    # Adicionar cards de métricas de Organic Search
    organic_metric_configs = [
        ('sessions', 'Sessões', '🔍', 0),
        ('users', 'Usuários', '👥', 0),
        ('new_users', 'Novos Usuários', '✨', 0),
        ('conversions', 'Conversões', '🎯', 1),
        ('revenue', 'Receita (R$)', '💰', 2),
        ('engagement_rate', 'Taxa de Engajamento', '❤️', 2),
        ('bounce_rate', 'Taxa de Rejeição', '↩️', 2),
        ('avg_session_duration', 'Duração Média (seg)', '⏱️', 0)
    ]
    
    for metric_key, label, icon, decimals in organic_metric_configs:
        m = organic_search_metrics[metric_key]
        html += f"""
                        <div class="metric-card" style="border-left: 4px solid #22c55e;">
                            <div class="metric-label">{icon} {label}</div>
                            <div class="metric-value">{format_number(m['current'], decimals)}</div>
                            <div class="metric-comparison">
                                {format_variation(m['variation'])} vs período anterior
                                <br><small>Anterior: {format_number(m['previous'], decimals)}</small>
                            </div>
                        </div>
        """
    
    html += """
                    </div>
                </div>
    """
    
    # Alertas e Diagnóstico
    sessions_var = organic_search_metrics['sessions']['variation']
    
    if sessions_var < -20:
        alert_class = 'alert-danger'
        alert_icon = '🚨'
        alert_title = 'ALERTA CRÍTICO'
        alert_msg = f'Queda significativa de {abs(sessions_var):.1f}% nas sessões orgânicas. Investigação urgente necessária.'
    elif sessions_var < 0:
        alert_class = 'alert-warning'
        alert_icon = '⚠️'
        alert_title = 'ATENÇÃO'
        alert_msg = f'Redução de {abs(sessions_var):.1f}% nas sessões orgânicas. Monitoramento recomendado.'
    else:
        alert_class = 'alert-success'
        alert_icon = '✅'
        alert_title = 'DESEMPENHO POSITIVO'
        alert_msg = f'Crescimento de {sessions_var:.1f}% nas sessões orgânicas. Continue o bom trabalho!'
    
    html += f"""
                <div class="alert {alert_class}">
                    <strong>{alert_icon} {alert_title}</strong>
                    <p>{alert_msg}</p>
                </div>
    """
    
    # Análise por Dispositivo
    html += """
                <div class="section">
                    <h2 class="section-title">📱 Análise por Dispositivo</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Dispositivo</th>
                                <th>Sessões (Atual)</th>
                                <th>Sessões (Anterior)</th>
                                <th>Variação</th>
                                <th>Usuários (Atual)</th>
                                <th>Receita (Atual)</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for device, row in comparison_device.iterrows():
        html += f"""
                            <tr>
                                <td><strong>{device}</strong></td>
                                <td>{format_number(row['sessions_current'])}</td>
                                <td>{format_number(row['sessions_previous'])}</td>
                                <td>{format_variation(row['sessions_var_%'])}</td>
                                <td>{format_number(row['users_current'])}</td>
                                <td>R$ {format_number(row['revenue_current'], 2)}</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
    """
    
    # Análise por Source/Medium
    html += """
                <div class="section">
                    <h2 class="section-title">🔗 Análise por Fonte (Source/Medium)</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Fonte / Meio</th>
                                <th>Sessões (Atual)</th>
                                <th>Sessões (Anterior)</th>
                                <th>Variação</th>
                                <th>Usuários</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for source, row in comparison_source.head(10).iterrows():
        html += f"""
                            <tr>
                                <td><strong>{source}</strong></td>
                                <td>{format_number(row['sessions_current'])}</td>
                                <td>{format_number(row['sessions_previous'])}</td>
                                <td>{format_variation(row['sessions_var_%'])}</td>
                                <td>{format_number(row['users_current'])}</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
    """
    
    # Landing Pages
    html += """
                <div class="section">
                    <h2 class="section-title">🎯 Top Landing Pages - Período Atual</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Landing Page</th>
                                <th>Sessões</th>
                                <th>Usuários</th>
                                <th>Taxa de Rejeição</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for _, row in landing_current.head(10).iterrows():
        html += f"""
                            <tr>
                                <td><code>{row['landing_page'][:80]}</code></td>
                                <td>{format_number(row['sessions'])}</td>
                                <td>{format_number(row['users'])}</td>
                                <td>{row['bounce_rate']:.2f}%</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
    """
    
    # Filtros Aplicados
    html += f"""
                <div class="section">
                    <h2 class="section-title">⚙️ Configuração do Relatório</h2>
                    <p><strong>Propriedade GA4:</strong> {Config.PROPERTY_ID}</p>
                    <p><strong>Fontes Orgânicas Incluídas:</strong></p>
                    <ul>
    """
    
    for source in Config.ORGANIC_SOURCES:
        html += f"<li><code>{source}</code></li>"
    
    html += """
                    </ul>
                </div>
                
            </div>
            
            <footer>
                <p><strong>GA4 Organic Traffic Analyzer</strong> v2.0</p>
                <p>Relatório gerado automaticamente | Dados extraídos via Google Analytics Data API</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    logger.info("✓ Relatório HTML gerado com sucesso")
    return html

# ============================================================================
# EXPORTAÇÃO
# ============================================================================

def export_to_excel(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
    metrics: Dict,
    comparison_device: pd.DataFrame,
    comparison_source: pd.DataFrame,
    landing_current: pd.DataFrame,
    landing_previous: pd.DataFrame
) -> str:
    """
    Exporta dados para arquivo Excel com múltiplas abas
    
    Args:
        df_current: Dados período atual
        df_previous: Dados período anterior
        metrics: Métricas comparativas
        comparison_device: Comparação por dispositivo
        comparison_source: Comparação por fonte
        landing_current: Landing pages atuais
        landing_previous: Landing pages anteriores
        
    Returns:
        Caminho do arquivo gerado
    """
    try:
        logger.info("Exportando dados para Excel")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ga4_organic_report_{timestamp}.xlsx'
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        # Criar resumo de métricas
        metrics_df = pd.DataFrame([
            {
                'Métrica': 'Sessões',
                'Atual': metrics['sessions']['current'],
                'Anterior': metrics['sessions']['previous'],
                'Variação (%)': metrics['sessions']['variation'],
                'Variação (Abs)': metrics['sessions']['variation_abs']
            },
            {
                'Métrica': 'Usuários',
                'Atual': metrics['users']['current'],
                'Anterior': metrics['users']['previous'],
                'Variação (%)': metrics['users']['variation'],
                'Variação (Abs)': metrics['users']['variation_abs']
            },
            {
                'Métrica': 'Novos Usuários',
                'Atual': metrics['new_users']['current'],
                'Anterior': metrics['new_users']['previous'],
                'Variação (%)': metrics['new_users']['variation'],
                'Variação (Abs)': metrics['new_users']['variation_abs']
            },
            {
                'Métrica': 'Conversões',
                'Atual': metrics['conversions']['current'],
                'Anterior': metrics['conversions']['previous'],
                'Variação (%)': metrics['conversions']['variation'],
                'Variação (Abs)': metrics['conversions']['variation_abs']
            },
            {
                'Métrica': 'Receita',
                'Atual': metrics['revenue']['current'],
                'Anterior': metrics['revenue']['previous'],
                'Variação (%)': metrics['revenue']['variation'],
                'Variação (Abs)': metrics['revenue']['variation_abs']
            },
            {
                'Métrica': 'Taxa de Engajamento',
                'Atual': metrics['engagement_rate']['current'],
                'Anterior': metrics['engagement_rate']['previous'],
                'Variação (%)': metrics['engagement_rate']['variation'],
                'Variação (Abs)': metrics['engagement_rate']['variation_abs']
            },
            {
                'Métrica': 'Taxa de Rejeição',
                'Atual': metrics['bounce_rate']['current'],
                'Anterior': metrics['bounce_rate']['previous'],
                'Variação (%)': metrics['bounce_rate']['variation'],
                'Variação (Abs)': metrics['bounce_rate']['variation_abs']
            }
        ])
        
        # Exportar para Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            metrics_df.to_excel(writer, sheet_name='Resumo Comparativo', index=False)
            comparison_device.to_excel(writer, sheet_name='Por Dispositivo')
            comparison_source.to_excel(writer, sheet_name='Por Fonte')
            df_current.to_excel(writer, sheet_name='Dados Atuais', index=False)
            df_previous.to_excel(writer, sheet_name='Dados Anteriores', index=False)
            landing_current.to_excel(writer, sheet_name='Landing Pages Atual', index=False)
            landing_previous.to_excel(writer, sheet_name='Landing Pages Anterior', index=False)
        
        logger.info(f"✓ Dados exportados para: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Erro ao exportar Excel: {str(e)}", exc_info=True)
        return ""

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Função principal que orquestra toda a análise
    """
    try:
        logger.info("Iniciando análise de tráfego orgânico")
        
        # Verificar arquivo de credenciais
        if not os.path.exists(Config.CLIENT_SECRET_FILE):
            logger.error(f"Arquivo de credenciais não encontrado: {Config.CLIENT_SECRET_FILE}")
            logger.error("Baixe as credenciais OAuth 2.0 do Google Cloud Console")
            return
        
        # Autenticação
        client = authenticate_ga4()
        if not client:
            logger.error("Falha na autenticação. Abortando.")
            return
        
        # Criar diretório de saída
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # Coleta de dados - Período Atual
        logger.info("\n" + "="*80)
        logger.info("COLETANDO DADOS DO PERÍODO ATUAL")
        logger.info("="*80)
        
        df_current = fetch_organic_traffic_data(
            client, 
            Config.CURRENT_PERIOD_START, 
            Config.CURRENT_PERIOD_END,
            "Atual"
        )
        
        df_organic_search_current = fetch_organic_search_data(
            client,
            Config.CURRENT_PERIOD_START,
            Config.CURRENT_PERIOD_END,
            "Atual"
        )
        
        landing_current = fetch_landing_pages(
            client,
            Config.CURRENT_PERIOD_START,
            Config.CURRENT_PERIOD_END,
            "Atual"
        )
        
        # Coleta de dados - Período Anterior
        logger.info("\n" + "="*80)
        logger.info("COLETANDO DADOS DO PERÍODO ANTERIOR")
        logger.info("="*80)
        
        df_previous = fetch_organic_traffic_data(
            client,
            Config.PREVIOUS_PERIOD_START,
            Config.PREVIOUS_PERIOD_END,
            "Anterior"
        )
        
        df_organic_search_previous = fetch_organic_search_data(
            client,
            Config.PREVIOUS_PERIOD_START,
            Config.PREVIOUS_PERIOD_END,
            "Anterior"
        )
        
        landing_previous = fetch_landing_pages(
            client,
            Config.PREVIOUS_PERIOD_START,
            Config.PREVIOUS_PERIOD_END,
            "Anterior"
        )
        
        # Verificar se há dados
        if df_current is None or df_previous is None:
            logger.error("Falha ao coletar dados de um ou ambos períodos")
            return
        
        if df_organic_search_current is None or df_organic_search_previous is None:
            logger.warning("Falha ao coletar dados de Organic Search")
            df_organic_search_current = pd.DataFrame()
            df_organic_search_previous = pd.DataFrame()
        
        if df_current.empty or df_previous.empty:
            logger.warning("Um ou ambos os períodos não possuem dados")
            logger.info(f"Registros período atual: {len(df_current)}")
            logger.info(f"Registros período anterior: {len(df_previous)}")
        
        # Análise comparativa
        logger.info("\n" + "="*80)
        logger.info("REALIZANDO ANÁLISE COMPARATIVA")
        logger.info("="*80)
        
        metrics = calculate_comparison_metrics(df_current, df_previous)
        
        # Calcular métricas de Organic Search
        if not df_organic_search_current.empty and not df_organic_search_previous.empty:
            organic_search_metrics = calculate_comparison_metrics(
                df_organic_search_current, 
                df_organic_search_previous
            )
        else:
            # Métricas vazias se não houver dados
            organic_search_metrics = {
                key: {'current': 0, 'previous': 0, 'variation': 0, 'variation_abs': 0}
                for key in ['sessions', 'users', 'new_users', 'conversions', 'revenue', 
                           'engagement_rate', 'bounce_rate', 'avg_session_duration']
            }
        
        comparison_device = analyze_by_dimension(df_current, df_previous, 'device')
        comparison_source = analyze_by_dimension(df_current, df_previous, 'source_medium')
        
        # Gerar relatório HTML
        logger.info("\n" + "="*80)
        logger.info("GERANDO RELATÓRIOS")
        logger.info("="*80)
        
        html_content = generate_html_report(
            metrics,
            organic_search_metrics,
            df_current,
            df_previous,
            comparison_device,
            comparison_source,
            landing_current if landing_current is not None else pd.DataFrame(),
            landing_previous if landing_previous is not None else pd.DataFrame()
        )
        
        # Salvar HTML
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f'ga4_organic_report_{timestamp}.html'
        html_filepath = os.path.join(Config.OUTPUT_DIR, html_filename)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ Relatório HTML salvo: {html_filepath}")
        
        # Exportar Excel
        excel_path = export_to_excel(
            df_current,
            df_previous,
            metrics,
            comparison_device,
            comparison_source,
            landing_current if landing_current is not None else pd.DataFrame(),
            landing_previous if landing_previous is not None else pd.DataFrame()
        )
        
        # Resumo final
        logger.info("\n" + "="*80)
        logger.info("ANÁLISE CONCLUÍDA COM SUCESSO")
        logger.info("="*80)
        logger.info(f"📄 Relatório HTML: {html_filepath}")
        logger.info(f"📊 Planilha Excel: {excel_path}")
        logger.info(f"📝 Log completo: {os.path.join(Config.OUTPUT_DIR, Config.LOG_FILE)}")
        logger.info("\n🎯 Principais Resultados:")
        logger.info(f"   Sessões: {metrics['sessions']['current']:,.0f} ({metrics['sessions']['variation']:+.2f}%)")
        logger.info(f"   Usuários: {metrics['users']['current']:,.0f} ({metrics['users']['variation']:+.2f}%)")
        logger.info(f"   Receita: R$ {metrics['revenue']['current']:,.2f} ({metrics['revenue']['variation']:+.2f}%)")
        logger.info("\n🌿 Organic Search:")
        logger.info(f"   Sessões: {organic_search_metrics['sessions']['current']:,.0f} ({organic_search_metrics['sessions']['variation']:+.2f}%)")
        logger.info(f"   Usuários: {organic_search_metrics['users']['current']:,.0f} ({organic_search_metrics['users']['variation']:+.2f}%)")
        logger.info(f"   Receita: R$ {organic_search_metrics['revenue']['current']:,.2f} ({organic_search_metrics['revenue']['variation']:+.2f}%)")
        
    except Exception as e:
        logger.error(f"Erro crítico na execução: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()