import subprocess
import sys
from importlib.metadata import version, PackageNotFoundError

PACKAGE_NAME = "arcade"
REQUIRED_VERSION = "3.3.3"

def install_specific_version(package, version_num):
    print(f"Tentando instalar {package}=={version_num}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", f"{package}=={version_num}"])
        print(f"{package}=={version_num} instalado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Falha ao instalar {package}=={version_num}. Erro: {e}")
        sys.exit(1)

def check_and_install_arcade():
    try:
        installed_version = version(PACKAGE_NAME)
        print(f"Versão do {PACKAGE_NAME} instalada: {installed_version}")

        if installed_version == REQUIRED_VERSION:
            print(f"A versão {REQUIRED_VERSION} do {PACKAGE_NAME} já está instalada. Nada a fazer.")
        else:
            print(f"Versão incorreta ({installed_version}) encontrada. Desinstalando e instalando a versão {REQUIRED_VERSION}...")
            install_specific_version(PACKAGE_NAME, REQUIRED_VERSION)

    except PackageNotFoundError:
        print(f"O pacote {PACKAGE_NAME} não foi encontrado. Instalando a versão {REQUIRED_VERSION}...")
        install_specific_version(PACKAGE_NAME, REQUIRED_VERSION)
    except Exception as e:
        print(f"Ocorreu um erro ao verificar a versão: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_and_install_arcade()
    
    import arcade
    print(f"Script pronto para usar arcade versão {arcade.__version__}")
