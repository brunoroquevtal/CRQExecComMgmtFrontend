"""
Script auxiliar para ajudar a obter URL de download do SharePoint
Abre o navegador e fornece instruções passo a passo
"""
import webbrowser
import sys
import os

SHAREPOINT_URL = "https://vtalcorp.sharepoint.com/:x:/r/teams/msteams_490a4b_015830/gerplanejamentoinfra/Documentos%20Compartilhados/Arquitetura%20de%20Infraestrutura/Moving%20Datacenter%20ELEA/Projeto/11.%20CRQs/CRQ%20Migra%C3%A7%C3%A3o%20Rede%20SCN%20-%20ARCOS/CRQ%20VIRADA%20REDE.xlsx?d=w274473ebda45412681c315403ca9c9dc&csf=1&web=1&e=Oyp0pX"

def main():
    print("=" * 70)
    print("📥 ASSISTENTE DE DOWNLOAD DO SHAREPOINT")
    print("=" * 70)
    print()
    print("Este script vai abrir o SharePoint no navegador.")
    print("Siga as instruções abaixo para baixar o arquivo:")
    print()
    print("📋 INSTRUÇÕES:")
    print("1. O SharePoint será aberto no seu navegador")
    print("2. Faça login se necessário")
    print("3. Quando o arquivo abrir, clique em 'Arquivo' (File) no canto superior")
    print("4. Selecione 'Salvar como' → 'Baixar uma cópia'")
    print("5. O arquivo será baixado para sua pasta de Downloads")
    print("6. Depois execute:")
    print()
    print(f"   python sync_excel.py \"$env:USERPROFILE\\Downloads\\CRQ VIRADA REDE.xlsx\"")
    print()
    print("=" * 70)
    
    resposta = input("Deseja abrir o SharePoint agora? (s/n): ").lower().strip()
    
    if resposta in ('s', 'sim', 'y', 'yes'):
        print("\n🌐 Abrindo SharePoint no navegador...")
        webbrowser.open(SHAREPOINT_URL)
        print("✓ Navegador aberto!")
        print()
        print("💡 Dica: Após baixar, você pode executar:")
        print(f"   python sync_excel.py \"$env:USERPROFILE\\Downloads\\CRQ VIRADA REDE.xlsx\"")
    else:
        print("\n❌ Operação cancelada.")
        print("Você pode abrir manualmente:")
        print(SHAREPOINT_URL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(0)
