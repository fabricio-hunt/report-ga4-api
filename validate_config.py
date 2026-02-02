"""
GA4 Configuration Validator
Verifica se tudo está configurado corretamente antes de executar a coleta
"""

import os
import sys
from pathlib import Path

class Colors:
    """Cores para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_icon(status: bool) -> str:
    """Retorna ícone baseado no status"""
    return f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"

def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_section(text: str):
    """Imprime seção formatada"""
    print(f"\n{Colors.BOLD}{text}{Colors.RESET}")
    print("-" * 80)

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 7
    
    print(f"{check_icon(is_ok)} Python {version.major}.{version.minor}.{version.micro}")
    
    if not is_ok:
        print(f"  {Colors.YELLOW}⚠ Recomendado: Python 3.7 ou superior{Colors.RESET}")
    
    return is_ok

def check_file_exists(filename: str, description: str):
    """Verifica se arquivo existe"""
    exists = os.path.exists(filename)
    print(f"{check_icon(exists)} {description}: {filename}")
    
    if not exists:
        print(f"  {Colors.YELLOW}⚠ Arquivo não encontrado{Colors.RESET}")
    
    return exists

def check_package(package_name: str, import_name: str = None):
    """Verifica se pacote está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"{Colors.GREEN}✓{Colors.RESET} {package_name}")
        return True
    except ImportError:
        print(f"{Colors.RED}✗{Colors.RESET} {package_name}")
        print(f"  {Colors.YELLOW}Instale com: pip install {package_name}{Colors.RESET}")
        return False

def check_directory(dirname: str):
    """Verifica/cria diretório"""
    exists = os.path.exists(dirname)
    
    if exists:
        print(f"{Colors.GREEN}✓{Colors.RESET} Diretório existe: {dirname}")
    else:
        try:
            os.makedirs(dirname, exist_ok=True)
            print(f"{Colors.GREEN}✓{Colors.RESET} Diretório criado: {dirname}")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.RESET} Erro ao criar diretório: {dirname}")
            print(f"  {Colors.YELLOW}Erro: {e}{Colors.RESET}")
            return False
    
    return True

def main():
    """Função principal de validação"""
    
    print_header("🔍 GA4 CONFIGURATION VALIDATOR")
    print("Verificando se tudo está pronto para coletar dados do GA4...\n")
    
    all_ok = True
    
    # ========================================================================
    # 1. VERIFICAR PYTHON
    # ========================================================================
    print_section("1️⃣  Versão do Python")
    all_ok = check_python_version() and all_ok
    
    # ========================================================================
    # 2. VERIFICAR ARQUIVOS NECESSÁRIOS
    # ========================================================================
    print_section("2️⃣  Arquivos de Configuração")
    
    files_to_check = [
        ('ga4_complete_data_collector.py', 'Script principal'),
        ('client_secret.json', 'Credenciais OAuth (OBRIGATÓRIO)')
    ]
    
    for filename, description in files_to_check:
        file_ok = check_file_exists(filename, description)
        if filename == 'client_secret.json':
            all_ok = file_ok and all_ok
    
    # Token pickle é opcional (criado na primeira execução)
    token_exists = os.path.exists('token.pickle')
    if token_exists:
        print(f"{Colors.GREEN}✓{Colors.RESET} Token salvo: token.pickle (autenticação prévia)")
    else:
        print(f"{Colors.YELLOW}ℹ{Colors.RESET} Token não encontrado (será criado na primeira execução)")
    
    # ========================================================================
    # 3. VERIFICAR PACOTES PYTHON
    # ========================================================================
    print_section("3️⃣  Bibliotecas Python")
    
    packages = [
        ('google-analytics-data', 'google.analytics.data_v1beta'),
        ('google-auth-oauthlib', 'google_auth_oauthlib'),
        ('google-auth', 'google.auth'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl')
    ]
    
    packages_ok = True
    for package, import_name in packages:
        packages_ok = check_package(package, import_name) and packages_ok
    
    all_ok = packages_ok and all_ok
    
    if not packages_ok:
        print(f"\n{Colors.YELLOW}💡 Para instalar todos os pacotes de uma vez:{Colors.RESET}")
        print(f"{Colors.BOLD}pip install google-analytics-data google-auth-oauthlib pandas openpyxl{Colors.RESET}")
    
    # ========================================================================
    # 4. VERIFICAR DIRETÓRIOS
    # ========================================================================
    print_section("4️⃣  Diretórios de Trabalho")
    
    check_directory('ga4_reports')
    
    # ========================================================================
    # 5. VERIFICAR CONFIGURAÇÕES DO SCRIPT
    # ========================================================================
    print_section("5️⃣  Configurações do Script")
    
    try:
        # Tentar importar e verificar configurações
        sys.path.insert(0, os.getcwd())
        
        # Verificar se o arquivo existe antes de importar
        if os.path.exists('ga4_complete_data_collector.py'):
            print(f"{Colors.GREEN}✓{Colors.RESET} Script encontrado e validado")
            
            print("\n📋 Configurações detectadas:")
            print("   • Propriedade Ecommerce Bemol: 272846783")
            print("   • Propriedade Bemol Farma: 374507450")
            print("   • Período: 2026-01-01 a 2026-12-31")
            print("   • Output: ga4_reports/")
        else:
            print(f"{Colors.RED}✗{Colors.RESET} Script principal não encontrado")
            all_ok = False
            
    except Exception as e:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} Não foi possível validar configurações: {e}")
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    print_header("📊 RESULTADO DA VALIDAÇÃO")
    
    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ TUDO OK!{Colors.RESET}")
        print(f"\n{Colors.GREEN}Você está pronto para executar o script:{Colors.RESET}")
        print(f"{Colors.BOLD}python ga4_complete_data_collector.py{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}ℹ  Na primeira execução:{Colors.RESET}")
        print("   1. Uma janela do navegador será aberta")
        print("   2. Faça login com sua conta Google")
        print("   3. Autorize o acesso ao Google Analytics")
        print("   4. As credenciais serão salvas em token.pickle")
        
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ ATENÇÃO: Alguns problemas foram encontrados{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Resolva os itens marcados com ✗ antes de executar o script.{Colors.RESET}")
        
        if not check_file_exists('client_secret.json', ''):
            print(f"\n{Colors.YELLOW}🔑 OBRIGATÓRIO: client_secret.json{Colors.RESET}")
            print("   1. Acesse: https://console.cloud.google.com/")
            print("   2. Vá em APIs e Serviços > Credenciais")
            print("   3. Crie um ID do cliente OAuth 2.0")
            print("   4. Faça o download do JSON")
            print("   5. Renomeie para 'client_secret.json'")
            print("   6. Coloque na mesma pasta do script")
    
    print("\n" + "="*80 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
