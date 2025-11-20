import subprocess
import time
import sys

print("⏳ Aguardando conclusão do registro Microsoft.Web...")
print("Isso pode levar 1-2 minutos.\n")

max_tentativas = 24  # 2 minutos (5 segundos x 24)
tentativa = 0

while tentativa < max_tentativas:
    try:
        result = subprocess.run(
            ['az', 'provider', 'show', '-n', 'Microsoft.Web', '--query', 'registrationState', '-o', 'tsv'],
            capture_output=True,
            text=True,
            check=True
        )
        
        status = result.stdout.strip()
        tentativa += 1
        
        if status == 'Registered':
            print(f"\n✅ Registro concluído com sucesso!")
            sys.exit(0)
        else:
            print(f"Tentativa {tentativa}/{max_tentativas}: Status = {status}", end='\r')
            time.sleep(5)
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

print(f"\n⚠️ Timeout após {max_tentativas * 5} segundos. Execute novamente: az provider show -n Microsoft.Web")
sys.exit(1)
