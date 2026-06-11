"""
GA4 Configuration Validator
Verifica se tudo está configurado corretamente antes de executar a coleta.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config, get_yaml_config, resolve_credential_path
from src.io.paths import is_databricks, resolve_output_dir


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def check_icon(status: bool) -> str:
    return f"{Colors.GREEN}[OK]{Colors.RESET}" if status else f"{Colors.RED}[X]{Colors.RESET}"


def print_header(text: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_section(text: str) -> None:
    print(f"\n{Colors.BOLD}{text}{Colors.RESET}")
    print("-" * 80)


def check_python_version() -> bool:
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 7
    print(f"{check_icon(is_ok)} Python {version.major}.{version.minor}.{version.micro}")
    if not is_ok:
        print(f"  {Colors.YELLOW}Recomendado: Python 3.7 ou superior{Colors.RESET}")
    return is_ok


def check_file_exists(filename: str, description: str) -> bool:
    exists = os.path.exists(filename)
    print(f"{check_icon(exists)} {description}: {filename}")
    if not exists:
        print(f"  {Colors.YELLOW}Arquivo não encontrado{Colors.RESET}")
    return exists


def check_package(package_name: str, import_name: str | None = None) -> bool:
    import_name = import_name or package_name
    try:
        __import__(import_name)
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {package_name}")
        return True
    except ImportError:
        print(f"{Colors.RED}[X]{Colors.RESET} {package_name}")
        print(f"  {Colors.YELLOW}Instale com: pip install {package_name}{Colors.RESET}")
        return False


def check_local_auth(config: Config) -> bool:
    secret_path = resolve_credential_path(config.client_secret_file)
    token_path = resolve_credential_path(config.token_file)

    secret_ok = check_file_exists(secret_path, "Credenciais OAuth (OBRIGATÓRIO)")
    token_ok = os.path.exists(token_path)
    if token_ok:
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Token salvo: {token_path}")
    else:
        print(
            f"{Colors.YELLOW}[i]{Colors.RESET} Token não encontrado "
            "(será criado na primeira execução local)"
        )
    return secret_ok


def check_databricks_auth(config: Config) -> bool:
    print(f"{check_icon(True)} Ambiente Databricks detectado")
    print(f"  Secret scope esperado: {config.secret_scope}")
    print(f"  Keys: {config.client_secret_key}, {config.refresh_token_key}")
    print(
        f"  {Colors.YELLOW}Secrets devem ser configurados manualmente no workspace.{Colors.RESET}"
    )
    return True


def check_output_dir() -> bool:
    try:
        output_dir = resolve_output_dir()
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Diretorio de saida: {output_dir}")
        return True
    except Exception as exc:
        print(f"{Colors.RED}[X]{Colors.RESET} Erro ao resolver diretorio de saida: {exc}")
        return False


def check_project_structure() -> bool:
    required = [
        "src/config.py",
        "src/auth.py",
        "src/io/paths.py",
        "src/export/excel.py",
        "jobs/run_main.py",
        "jobs/run_bemol_app.py",
        "jobs/run_farma_comparacao.py",
        "config/default.yaml",
    ]
    all_ok = True
    for rel_path in required:
        path = PROJECT_ROOT / rel_path
        ok = path.exists()
        print(f"{check_icon(ok)} {rel_path}")
        all_ok = all_ok and ok
    return all_ok


def check_yaml_config() -> bool:
    try:
        cfg = get_yaml_config()
        properties = cfg.get("properties", {})
        print(f"{Colors.GREEN}[OK]{Colors.RESET} config/default.yaml carregado")
        print(f"   - Ecommerce Bemol: {properties.get('ecommerce_bemol')}")
        print(f"   - Bemol Farma: {properties.get('bemol_farma')}")
        main_period = cfg.get("periods", {}).get("main", {})
        print(
            f"   - Periodo main: {main_period.get('analysis_start')} "
            f"a {main_period.get('analysis_end')}"
        )
        return True
    except Exception as exc:
        print(f"{Colors.RED}[X]{Colors.RESET} Erro ao carregar YAML: {exc}")
        return False


def main() -> int:
    print_header("GA4 CONFIGURATION VALIDATOR")
    print("Verificando se tudo está pronto para coletar dados do GA4...\n")

    all_ok = True
    config = Config.from_env(profile="main")

    print_section("1. Versão do Python")
    all_ok = check_python_version() and all_ok

    print_section("2. Estrutura do Projeto")
    all_ok = check_project_structure() and all_ok

    print_section("3. Configuração YAML")
    all_ok = check_yaml_config() and all_ok

    print_section("4. Autenticação")
    if is_databricks():
        all_ok = check_databricks_auth(config) and all_ok
    else:
        all_ok = check_local_auth(config) and all_ok

    print_section("5. Bibliotecas Python")
    packages = [
        ("google-analytics-data", "google.analytics.data_v1beta"),
        ("google-auth-oauthlib", "google_auth_oauthlib"),
        ("google-auth", "google.auth"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("pyyaml", "yaml"),
    ]
    packages_ok = True
    for package, import_name in packages:
        packages_ok = check_package(package, import_name) and packages_ok
    all_ok = packages_ok and all_ok

    if not packages_ok:
        print(f"\n{Colors.YELLOW}Para instalar todas as dependências:{Colors.RESET}")
        print(f"{Colors.BOLD}pip install -r requirements.txt{Colors.RESET}")

    print_section("6. Diretório de Saída Excel")
    all_ok = check_output_dir() and all_ok

    print_header("RESULTADO DA VALIDAÇÃO")

    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}TUDO OK!{Colors.RESET}")
        print(f"\n{Colors.GREEN}Comandos disponíveis:{Colors.RESET}")
        print(f"{Colors.BOLD}python jobs/run_main.py{Colors.RESET}")
        print(f"{Colors.BOLD}python jobs/run_bemol_app.py{Colors.RESET}")
        print(f"{Colors.BOLD}python jobs/run_farma_comparacao.py{Colors.RESET}")
        if not is_databricks():
            print(f"\n{Colors.BLUE}Na primeira execução local:{Colors.RESET}")
            print("   1. Uma janela do navegador será aberta")
            print("   2. Faça login com sua conta Google")
            print("   3. Autorize o acesso ao Google Analytics")
            print("   4. As credenciais serão salvas em token.pickle")
            print("   5. Execute tools/extract_refresh_token.py para configurar o Databricks")
    else:
        print(f"{Colors.RED}{Colors.BOLD}ATENÇÃO: Alguns problemas foram encontrados{Colors.RESET}")
        print(
            f"\n{Colors.YELLOW}Resolva os itens marcados com [X] antes de executar.{Colors.RESET}"
        )

    print("\n" + "=" * 80 + "\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
