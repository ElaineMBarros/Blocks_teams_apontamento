$SERVER = "zwyhqouopquuta6vdefgzqatmu-4wt3acgsbsneboaodwlmudpbwu.datawarehouse.fabric.microsoft.com"
$DATABASE = "DW_Portal_Apontamento"

Write-Host "Obtendo token..."
$token = (az account get-access-token --resource https://database.windows.net --query accessToken -o tsv)

Write-Host "Token obtido!"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "resultados\dados_$timestamp.csv"

$query = "SELECT * FROM dbo.gold_999_portal_outsourcing_apontamento_ultimos_90_dias WHERE d_dt_data >= DATEADD(DAY, -90, GETDATE()) ORDER BY d_dt_data DESC"

Write-Host "Executando query..."

sqlcmd -S $SERVER -d $DATABASE -G -P $token -Q $query -s "," -W -o $outputFile

Write-Host "Concluido! Arquivo: $outputFile"
Get-Content $outputFile -TotalCount 5
