$SERVER = "zwyhqouopquuta6vdefgzqatmu-4wt3acgsbsneboaodwlmudpbwu.datawarehouse.fabric.microsoft.com"
$DATABASE = "DW_Portal_Apontamento"

Write-Host "Obtendo token..."
$token = (az account get-access-token --resource https://database.windows.net --query accessToken -o tsv)
Write-Host "Token obtido!"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "resultados\dados_$timestamp.csv"
$tempFile = "resultados\temp_$timestamp.txt"

$query = "SELECT * FROM dbo.gold_999_portal_outsourcing_apontamento_ultimos_90_dias WHERE d_dt_data >= DATEADD(DAY, -90, GETDATE()) ORDER BY d_dt_data DESC"

Write-Host "Executando query..."

# Extrair direto com UTF-8
sqlcmd -S $SERVER -d $DATABASE -G -P $token -Q $query -s "," -W -f 65001 -o $outputFile

Write-Host "Extração concluída!"

Write-Host "Concluido! Arquivo: $outputFile"
Write-Host "Total de linhas: $((Get-Content $outputFile).Count)"
Get-Content $outputFile -TotalCount 3
