import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# --- CONFIGURAÇÃO ---
PROPERTY_ID = '272846783'  # Removida a barra
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

# Período de análise solicitado
START_DATE = '2026-01-01'
END_DATE = '2026-01-15'

def authenticate():
    """Autentica e retorna o cliente GA4"""
    print(f"--- Iniciando Autenticação ---")
    print(f"Lendo credencial: {CLIENT_SECRET_FILE}")
    
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    client = BetaAnalyticsDataClient(credentials=creds)
    
    print(f"✓ Autenticação concluída!")
    return client

def get_traffic_by_channel(client):
    """Análise 1: Tráfego x Usuários x Receita por Canal"""
    print(f"\n📊 Coletando: Tráfego, Usuários e Receita por Canal...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="date")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="totalRevenue"),
            Metric(name="conversions"),
            Metric(name="engagementRate")
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        order_bys=[OrderBy(dimension={'dimension_name': 'date'})]
    )
    
    response = client.run_report(request=request)
    
    data = []
    for row in response.rows:
        data.append({
            'Canal': row.dimension_values[0].value,
            'Data': row.dimension_values[1].value,
            'Sessoes': int(row.metric_values[0].value),
            'Usuarios_Total': int(row.metric_values[1].value),
            'Usuarios_Novos': int(row.metric_values[2].value),
            'Receita': float(row.metric_values[3].value),
            'Conversoes': float(row.metric_values[4].value),
            'Taxa_Engajamento': float(row.metric_values[5].value)
        })
    
    return pd.DataFrame(data)

def get_device_breakdown(client):
    """Análise 2: Breakdown por Dispositivo"""
    print(f"\n📱 Coletando: Análise por Dispositivo...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="deviceCategory")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)]
    )
    
    response = client.run_report(request=request)
    
    data = []
    for row in response.rows:
        data.append({
            'Canal': row.dimension_values[0].value,
            'Dispositivo': row.dimension_values[1].value,
            'Sessoes': int(row.metric_values[0].value),
            'Usuarios': int(row.metric_values[1].value),
            'Duracao_Media': float(row.metric_values[2].value)
        })
    
    return pd.DataFrame(data)

def get_source_medium(client):
    """Análise 3: Source/Medium detalhado"""
    print(f"\n🔍 Coletando: Source/Medium detalhado...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="bounceRate")
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        order_bys=[OrderBy(metric={'metric_name': 'sessions'}, desc=True)],
        limit=50
    )
    
    response = client.run_report(request=request)
    
    data = []
    for row in response.rows:
        data.append({
            'Source': row.dimension_values[0].value,
            'Medium': row.dimension_values[1].value,
            'Sessoes': int(row.metric_values[0].value),
            'Usuarios': int(row.metric_values[1].value),
            'Taxa_Rejeicao': float(row.metric_values[2].value)
        })
    
    return pd.DataFrame(data)

def get_landing_pages(client):
    """Análise 4: Landing Pages orgânicas"""
    print(f"\n🎯 Coletando: Landing Pages do tráfego orgânico...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="landingPage")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers")
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        dimension_filter={
            'filter': {
                'field_name': 'sessionDefaultChannelGroup',
                'string_filter': {
                    'match_type': 'CONTAINS',
                    'value': 'Organic'
                }
            }
        },
        order_bys=[OrderBy(metric={'metric_name': 'sessions'}, desc=True)],
        limit=20
    )
    
    response = client.run_report(request=request)
    
    data = []
    for row in response.rows:
        data.append({
            'Landing_Page': row.dimension_values[0].value,
            'Sessoes': int(row.metric_values[0].value),
            'Usuarios': int(row.metric_values[1].value)
        })
    
    return pd.DataFrame(data)

def analyze_data(df_traffic, df_device, df_source, df_landing):
    """Realiza análises detalhadas dos dados"""
    
    print("\n" + "="*80)
    print("📈 RELATÓRIO DE ANÁLISE - TRÁFEGO ORGÂNICO")
    print(f"Período: {START_DATE} até {END_DATE}")
    print("="*80)
    
    # 1. RESUMO POR CANAL
    print("\n1️⃣ RESUMO GERAL POR CANAL DE AQUISIÇÃO")
    print("-" * 80)
    summary = df_traffic.groupby('Canal').agg({
        'Sessoes': 'sum',
        'Usuarios_Total': 'sum',
        'Usuarios_Novos': 'sum',
        'Receita': 'sum',
        'Conversoes': 'sum'
    }).sort_values('Sessoes', ascending=False)
    
    summary['% Sessoes'] = (summary['Sessoes'] / summary['Sessoes'].sum() * 100).round(2)
    summary['% Receita'] = (summary['Receita'] / summary['Receita'].sum() * 100).round(2)
    print(summary)
    
    # 2. ANÁLISE ESPECÍFICA DO ORGÂNICO
    print("\n2️⃣ ANÁLISE DO TRÁFEGO ORGÂNICO")
    print("-" * 80)
    organic_data = df_traffic[df_traffic['Canal'].str.contains('Organic', case=False, na=False)]
    
    if len(organic_data) > 0:
        organic_summary = organic_data.groupby('Data').agg({
            'Sessoes': 'sum',
            'Usuarios_Total': 'sum',
            'Receita': 'sum'
        })
        
        print(f"Total de Sessões Orgânicas: {organic_summary['Sessoes'].sum():,}")
        print(f"Total de Usuários Orgânicos: {organic_summary['Usuarios_Total'].sum():,}")
        print(f"Receita Orgânica: R$ {organic_summary['Receita'].sum():,.2f}")
        print(f"\nMédia Diária:")
        print(f"  - Sessões: {organic_summary['Sessoes'].mean():.0f}")
        print(f"  - Usuários: {organic_summary['Usuarios_Total'].mean():.0f}")
        print(f"  - Receita: R$ {organic_summary['Receita'].mean():.2f}")
        
        # Tendência
        if len(organic_summary) > 1:
            trend = ((organic_summary['Sessoes'].iloc[-1] - organic_summary['Sessoes'].iloc[0]) / 
                     organic_summary['Sessoes'].iloc[0] * 100)
            print(f"\nTendência do período: {trend:+.1f}%")
    else:
        print("⚠️ ALERTA: Nenhum dado de tráfego orgânico encontrado!")
    
    # 3. CANAIS QUE CRESCERAM
    print("\n3️⃣ CANAIS QUE CRESCERAM (TOP 5)")
    print("-" * 80)
    top_channels = summary.nlargest(5, 'Sessoes')[['Sessoes', '% Sessoes', 'Receita', '% Receita']]
    print(top_channels)
    
    # 4. ANÁLISE POR DISPOSITIVO
    print("\n4️⃣ BREAKDOWN POR DISPOSITIVO")
    print("-" * 80)
    device_summary = df_device.groupby(['Canal', 'Dispositivo']).agg({
        'Sessoes': 'sum',
        'Usuarios': 'sum'
    }).sort_values('Sessoes', ascending=False)
    print(device_summary.head(15))
    
    # Verificação crítica: Orgânico Mobile
    organic_mobile = df_device[
        (df_device['Canal'].str.contains('Organic', case=False, na=False)) & 
        (df_device['Dispositivo'] == 'mobile')
    ]['Sessoes'].sum()
    
    print(f"\n⚠️ VERIFICAÇÃO CRÍTICA:")
    print(f"Sessões Orgânicas Mobile: {organic_mobile:,}")
    if organic_mobile == 0:
        print("🚨 ALERTA VERMELHO: Zero tráfego orgânico mobile detectado!")
    
    # 5. SOURCE/MEDIUM DETALHADO
    print("\n5️⃣ TOP 10 SOURCE/MEDIUM")
    print("-" * 80)
    print(df_source.head(10))
    
    # 6. LANDING PAGES ORGÂNICAS
    print("\n6️⃣ TOP 10 LANDING PAGES ORGÂNICAS")
    print("-" * 80)
    print(df_landing.head(10))
    
    # 7. DIAGNÓSTICO E RECOMENDAÇÕES
    print("\n7️⃣ DIAGNÓSTICO E RECOMENDAÇÕES")
    print("-" * 80)
    
    organic_pct = summary.loc[summary.index.str.contains('Organic', case=False, na=False), '% Sessoes'].sum()
    
    print(f"Participação do Orgânico: {organic_pct:.2f}%")
    
    if organic_pct < 10:
        print("🔴 CRÍTICO: Tráfego orgânico abaixo de 10%")
        print("\nPossíveis causas:")
        print("  • Penalização do Google")
        print("  • Problemas técnicos de SEO")
        print("  • Migração forçada para App")
        print("  • Configuração incorreta do GA4")
    elif organic_pct < 20:
        print("🟡 ATENÇÃO: Tráfego orgânico baixo")
    else:
        print("🟢 OK: Tráfego orgânico dentro da normalidade")
    
    return summary, organic_summary if len(organic_data) > 0 else None

def create_visualizations(df_traffic, summary):
    """Cria visualizações dos dados"""
    print("\n📊 Gerando visualizações...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Análise GA4 - {START_DATE} a {END_DATE}', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Evolução diária por canal (top 5)
    top_channels = summary.nlargest(5, 'Sessoes').index.tolist()
    for channel in top_channels:
        channel_data = df_traffic[df_traffic['Canal'] == channel].groupby('Data')['Sessoes'].sum()
        axes[0, 0].plot(channel_data.index, channel_data.values, marker='o', label=channel)
    
    axes[0, 0].set_title('Evolução Diária de Sessões (Top 5 Canais)')
    axes[0, 0].set_xlabel('Data')
    axes[0, 0].set_ylabel('Sessões')
    axes[0, 0].legend()
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gráfico 2: Pizza - Distribuição de Sessões
    axes[0, 1].pie(summary['Sessoes'], labels=summary.index, autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Distribuição de Sessões por Canal')
    
    # Gráfico 3: Barra - Receita por Canal
    summary_top = summary.nlargest(8, 'Receita')
    axes[1, 0].barh(summary_top.index, summary_top['Receita'])
    axes[1, 0].set_title('Receita por Canal')
    axes[1, 0].set_xlabel('Receita (R$)')
    
    # Gráfico 4: Usuários vs Receita
    axes[1, 1].scatter(summary['Usuarios_Total'], summary['Receita'], s=summary['Sessoes']/10, alpha=0.6)
    for idx, row in summary.iterrows():
        axes[1, 1].annotate(idx, (row['Usuarios_Total'], row['Receita']))
    axes[1, 1].set_title('Usuários vs Receita (tamanho = sessões)')
    axes[1, 1].set_xlabel('Total de Usuários')
    axes[1, 1].set_ylabel('Receita (R$)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_file = f'ga4_analysis_{START_DATE}_to_{END_DATE}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico salvo: {output_file}")
    
    plt.show()

def export_to_excel(df_traffic, df_device, df_source, df_landing, summary):
    """Exporta todos os dados para Excel"""
    output_file = f'ga4_analysis_{START_DATE}_to_{END_DATE}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name='Resumo por Canal')
        df_traffic.to_excel(writer, sheet_name='Dados Diários', index=False)
        df_device.to_excel(writer, sheet_name='Por Dispositivo', index=False)
        df_source.to_excel(writer, sheet_name='Source Medium', index=False)
        df_landing.to_excel(writer, sheet_name='Landing Pages', index=False)
    
    print(f"✓ Dados exportados: {output_file}")

def main():
    # Autenticação
    client = authenticate()
    
    # Coleta de dados
    print(f"\n🔄 Coletando dados do GA4 (Propriedade: {PROPERTY_ID})...")
    print(f"Período: {START_DATE} até {END_DATE}")
    
    df_traffic = get_traffic_by_channel(client)
    df_device = get_device_breakdown(client)
    df_source = get_source_medium(client)
    df_landing = get_landing_pages(client)
    
    # Análise
    summary, organic_summary = analyze_data(df_traffic, df_device, df_source, df_landing)
    
    # Visualizações
    create_visualizations(df_traffic, summary)
    
    # Export
    export_to_excel(df_traffic, df_device, df_source, df_landing, summary)
    
    print("\n" + "="*80)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("="*80)

if __name__ == "__main__":
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ ERRO: Arquivo {CLIENT_SECRET_FILE} não encontrado!")
        print("Baixe as credenciais OAuth 2.0 do Google Cloud Console")
    else:
        main()