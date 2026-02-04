"""
Filtro de Dados GA4 - App (Android e iOS) - Ano 2025
Coleta dados filtrados para:
- Período: Janeiro a Dezembro de 2025
- Plataforma: Android OU iOS
- Métricas: Usuários totais, Sessões totais, Receita total
"""

import os
import logging
from datetime import datetime
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    FilterExpression, Filter
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import pandas as pd

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configurações para coleta de dados do App"""
    # ID da propriedade GA4 do Ecommerce Bemol (contém dados do App)
    PROPERTY_ID = '272846783'
    
    # Autenticação
    CLIENT_SECRET_FILE = 'client_secret.json'
    TOKEN_FILE = 'token.pickle'
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    
    # Período de análise - Ano 2025 completo
    ANALYSIS_START = '2025-01-01'
    ANALYSIS_END = '2025-12-31'
    
    # Output
    OUTPUT_DIR = 'ga4_reports'
    LOG_FILE = 'filtro_app_2025.log'

# ============================================================================
# LOGGING
# ============================================================================

def setup_logging():
    """Configura logging para arquivo e console"""
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    log_path = os.path.join(Config.OUTPUT_DIR, Config.LOG_FILE)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def authenticate_ga4():
    """
    Autentica no Google Analytics 4
    Retorna um cliente autenticado
    """
    creds = None
    
    # Verifica se já existe token salvo
    if os.path.exists(Config.TOKEN_FILE):
        logger.info("📂 Carregando credenciais salvas...")
        with open(Config.TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, faz login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("🔄 Renovando token expirado...")
            creds.refresh(Request())
        else:
            logger.info("🔐 Iniciando processo de autenticação...")
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.CLIENT_SECRET_FILE, Config.SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para próxima execução
        with open(Config.TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        logger.info("✅ Credenciais salvas com sucesso!")
    
    return BetaAnalyticsDataClient(credentials=creds)

# ============================================================================
# COLETA DE DADOS - APP (ANDROID E iOS)
# ============================================================================

def fetch_app_data_2025(client):
    """
    Coleta dados do App para 2025 (janeiro a dezembro)
    
    Filtros:
    - Plataforma: Android OU iOS
    - Período: 2025-01-01 a 2025-12-31
    
    Métricas:
    - App_Usuários_total (activeUsers)
    - App_Sessões_total (sessions)
    - App_Receita_total (totalRevenue)
    
    Dimensão: Mês (month)
    """
    logger.info("📱 Coletando dados do App (Android + iOS) - Ano 2025...")
    
    try:
        # Configuração do filtro: platform = 'Android' OR platform = 'iOS'
        filter_expression = FilterExpression(
            or_group={
                'expressions': [
                    FilterExpression(
                        filter=Filter(
                            field_name="platform",
                            string_filter=Filter.StringFilter(
                                match_type=Filter.StringFilter.MatchType.EXACT,
                                value="Android"
                            )
                        )
                    ),
                    FilterExpression(
                        filter=Filter(
                            field_name="platform",
                            string_filter=Filter.StringFilter(
                                match_type=Filter.StringFilter.MatchType.EXACT,
                                value="iOS"
                            )
                        )
                    )
                ]
            }
        )
        
        # Requisição à API
        request = RunReportRequest(
            property=f"properties/{Config.PROPERTY_ID}",
            dimensions=[Dimension(name="month")],
            metrics=[
                Metric(name="activeUsers"),  # App_Usuários_total
                Metric(name="sessions"),      # App_Sessões_total
                Metric(name="totalRevenue")   # App_Receita_total
            ],
            date_ranges=[DateRange(
                start_date=Config.ANALYSIS_START,
                end_date=Config.ANALYSIS_END
            )],
            dimension_filter=filter_expression
        )
        
        response = client.run_report(request)
        
        # Processa os dados
        data = []
        meses = {
            '01': 'janeiro', '02': 'fevereiro', '03': 'março',
            '04': 'abril', '05': 'maio', '06': 'junho',
            '07': 'julho', '08': 'agosto', '09': 'setembro',
            '10': 'outubro', '11': 'novembro', '12': 'dezembro'
        }
        
        for row in response.rows:
            mes_num = row.dimension_values[0].value
            mes_nome = meses.get(mes_num, mes_num)
            
            usuarios = int(row.metric_values[0].value)
            sessoes = int(row.metric_values[1].value)
            receita = float(row.metric_values[2].value)
            
            data.append({
                'Mês': mes_nome,
                'Ano': '2025',
                'App_Usuários_total': usuarios,
                'App_Sessões_total': sessoes,
                'App_Receita_total': receita
            })
            
            logger.info(f"  ✓ {mes_nome}/2025: {usuarios:,} usuários | {sessoes:,} sessões | R$ {receita:,.2f}")
        
        # Ordena por mês
        ordem_meses = list(meses.values())
        df = pd.DataFrame(data)
        df['ordem'] = df['Mês'].map({mes: i for i, mes in enumerate(ordem_meses)})
        df = df.sort_values('ordem').drop('ordem', axis=1)
        
        logger.info(f"✅ Coletados dados de {len(df)} meses")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erro ao coletar dados do App: {str(e)}")
        raise

# ============================================================================
# EXPORTAÇÃO
# ============================================================================

def export_to_excel(df):
    """Exporta os dados para Excel"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"App_Android_iOS_2025_{timestamp}.xlsx"
    filepath = os.path.join(Config.OUTPUT_DIR, filename)
    
    logger.info(f"💾 Exportando para Excel: {filename}")
    
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='App (Android + iOS)', index=False)
            
            # Formata a planilha
            worksheet = writer.sheets['App (Android + iOS)']
            
            # Ajusta largura das colunas
            worksheet.column_dimensions['A'].width = 12  # Mês
            worksheet.column_dimensions['B'].width = 8   # Ano
            worksheet.column_dimensions['C'].width = 20  # Usuários
            worksheet.column_dimensions['D'].width = 20  # Sessões
            worksheet.column_dimensions['E'].width = 20  # Receita
            
            # Formata valores de receita como moeda
            from openpyxl.styles import numbers
            for row in range(2, len(df) + 2):
                cell = worksheet[f'E{row}']
                cell.number_format = 'R$ #,##0.00'
        
        logger.info(f"✅ Arquivo salvo com sucesso: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"❌ Erro ao exportar Excel: {str(e)}")
        raise

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO COLETA DE DADOS - APP (ANDROID + iOS) - 2025")
    logger.info("=" * 70)
    
    try:
        # 1. Autenticação
        logger.info("\n📋 ETAPA 1/3: Autenticação")
        client = authenticate_ga4()
        logger.info("✅ Autenticação concluída")
        
        # 2. Coleta de dados
        logger.info("\n📋 ETAPA 2/3: Coleta de dados")
        logger.info(f"   Período: {Config.ANALYSIS_START} a {Config.ANALYSIS_END}")
        logger.info(f"   Filtro: Plataforma = 'Android' OU 'iOS'")
        df_app = fetch_app_data_2025(client)
        
        # 3. Exportação
        logger.info("\n📋 ETAPA 3/3: Exportação")
        filepath = export_to_excel(df_app)
        
        # Resumo final
        logger.info("\n" + "=" * 70)
        logger.info("✅ COLETA CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 70)
        logger.info(f"📊 Total de registros: {len(df_app)}")
        logger.info(f"📁 Arquivo gerado: {filepath}")
        logger.info(f"📅 Período: Janeiro a Dezembro de 2025")
        logger.info(f"📱 Plataformas: Android + iOS")
        
        # Estatísticas gerais
        total_usuarios = df_app['App_Usuários_total'].sum()
        total_sessoes = df_app['App_Sessões_total'].sum()
        total_receita = df_app['App_Receita_total'].sum()
        
        logger.info("\n📈 TOTAIS DO ANO 2025:")
        logger.info(f"   👥 Usuários: {total_usuarios:,}")
        logger.info(f"   📊 Sessões: {total_sessoes:,}")
        logger.info(f"   💰 Receita: R$ {total_receita:,.2f}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"\n❌ ERRO FATAL: {str(e)}")
        raise

if __name__ == "__main__":
    main()
