"""
Script para fazer upload do CSV para Azure Blob Storage
"""
import os
from azure.storage.blob import BlobServiceClient
from pathlib import Path

def upload_csv_to_azure():
    """Faz upload do CSV para Azure Blob Storage"""
    
    # Connection string do Azure Storage
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connection_string:
        print("❌ AZURE_STORAGE_CONNECTION_STRING não configurada!")
        print("\nConfigura assim:")
        print('$env:AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."')
        return False
    
    # Arquivo CSV local
    csv_file = Path("resultados/dados_anonimizados_decupado_20251118_211544.csv")
    
    if not csv_file.exists():
        print(f"❌ Arquivo não encontrado: {csv_file}")
        return False
    
    print(f"📁 Arquivo encontrado: {csv_file}")
    print(f"📏 Tamanho: {csv_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # Conectar ao Azure Storage
        print("\n🔗 Conectando ao Azure Storage...")
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        
        # Criar container se não existir
        container_name = "dados"
        print(f"📦 Verificando container '{container_name}'...")
        
        try:
            container_client = blob_service.get_container_client(container_name)
            container_client.get_container_properties()
            print(f"✅ Container '{container_name}' já existe")
        except:
            print(f"📦 Criando container '{container_name}'...")
            container_client = blob_service.create_container(container_name)
            print(f"✅ Container '{container_name}' criado")
        
        # Upload do arquivo
        blob_name = csv_file.name
        blob_client = container_client.get_blob_client(blob_name)
        
        print(f"\n⬆️ Fazendo upload de '{blob_name}'...")
        print("   (pode levar alguns minutos...)")
        
        with open(csv_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        print(f"\n✅ Upload concluído com sucesso!")
        print(f"\n📋 Informações do blob:")
        print(f"   Container: {container_name}")
        print(f"   Blob: {blob_name}")
        print(f"   URL: {blob_client.url}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no upload: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Upload CSV para Azure Blob Storage")
    print("=" * 60)
    
    success = upload_csv_to_azure()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCESSO! CSV disponível no Azure Storage")
        print("=" * 60)
        print("\n📝 Próximo passo:")
        print("   Configure a variável no Railway:")
        print("   AZURE_STORAGE_CONNECTION_STRING=sua_connection_string")
    else:
        print("\n" + "=" * 60)
        print("❌ FALHA no upload")
        print("=" * 60)
