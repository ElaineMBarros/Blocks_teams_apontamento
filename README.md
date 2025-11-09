# Blocks Teams - Apontamento de Horas

Aplicação Microsoft Teams para registro e gerenciamento de apontamentos de horas de trabalho.

## 📋 Descrição

Esta é uma aplicação de aba pessoal (Personal Tab) para Microsoft Teams que permite aos usuários registrar e acompanhar suas horas de trabalho em diferentes projetos. A aplicação oferece uma interface intuitiva e integrada ao Microsoft Teams.

## ✨ Funcionalidades

- ✅ Registro de apontamentos de horas por projeto
- ✅ Visualização de apontamentos recentes
- ✅ Resumo de horas trabalhadas
- ✅ Integração com Microsoft Teams
- ✅ Armazenamento local dos dados
- ✅ Interface responsiva e adaptada ao tema do Teams

## 🚀 Instalação e Configuração

### Pré-requisitos

- Node.js (versão 14 ou superior)
- npm (geralmente incluído com Node.js)
- Conta Microsoft Teams
- ngrok ou similar para expor o servidor local (para desenvolvimento)

### Passos para Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/ElaineMBarros/Blocks_teams_apontamento.git
   cd Blocks_teams_apontamento
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   ```

3. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.sample .env
   ```
   Edite o arquivo `.env` e configure:
   - `PORT`: Porta do servidor (padrão: 3000)
   - `TEAMS_APP_ID`: ID da sua aplicação Teams
   - `HOSTNAME`: URL pública do seu servidor

4. **Para desenvolvimento local com ngrok:**
   ```bash
   # Em um terminal, inicie o servidor
   npm start
   
   # Em outro terminal, inicie o ngrok
   ngrok http 3000
   ```
   Copie a URL do ngrok (ex: `https://abc123.ngrok.io`) e atualize:
   - O arquivo `.env` (variável `HOSTNAME`)
   - O arquivo `manifest/manifest.json` (substitua `{{HOSTNAME}}` pela URL)

5. **Configure o Teams App ID:**
   - Acesse o [Teams Developer Portal](https://dev.teams.microsoft.com/)
   - Crie uma nova aplicação
   - Copie o App ID e atualize:
     - Arquivo `.env`
     - Arquivo `manifest/manifest.json` (substitua `{{TEAMS_APP_ID}}`)

## 📦 Instalação no Microsoft Teams

1. **Prepare o pacote da aplicação:**
   - Atualize `manifest/manifest.json` com suas configurações
   - Crie um arquivo ZIP contendo:
     - `manifest.json`
     - `color.png`
     - `outline.png`

2. **Instale no Teams:**
   - Abra o Microsoft Teams
   - Vá para "Apps" → "Manage your apps" → "Upload an app"
   - Selecione "Upload a custom app"
   - Escolha o arquivo ZIP criado
   - Adicione a aplicação

## 🛠️ Uso

### Executar em Desenvolvimento

```bash
npm start
```

O servidor iniciará em `http://localhost:3000`

### Estrutura do Projeto

```
Blocks_teams_apontamento/
├── manifest/              # Configurações do Teams
│   ├── manifest.json     # Manifesto da aplicação
│   ├── color.png         # Ícone colorido (192x192)
│   └── outline.png       # Ícone outline (32x32)
├── public/               # Arquivos públicos
│   ├── css/
│   │   └── style.css    # Estilos da aplicação
│   ├── js/
│   │   └── app.js       # Lógica da aplicação
│   └── tab.html         # Página principal da aba
├── server.js            # Servidor Express
├── package.json         # Dependências do projeto
├── .env.sample          # Exemplo de variáveis de ambiente
├── .gitignore          # Arquivos ignorados pelo Git
└── README.md           # Este arquivo
```

## 🎯 Como Usar a Aplicação

1. **Adicionar um Apontamento:**
   - Preencha a data do trabalho
   - Insira a quantidade de horas
   - Digite o nome do projeto
   - Adicione uma descrição das atividades
   - Clique em "Adicionar Apontamento"

2. **Visualizar Apontamentos:**
   - Os apontamentos aparecem na seção "Apontamentos Recentes"
   - Ordenados por data (mais recentes primeiro)

3. **Acompanhar o Resumo:**
   - Veja o total de horas trabalhadas
   - Veja o número total de apontamentos

## 🔧 Tecnologias Utilizadas

- **Microsoft Teams JavaScript SDK** (v2.19.0) - Integração com Teams
- **Express.js** - Servidor web
- **HTML5/CSS3/JavaScript** - Interface do usuário
- **LocalStorage** - Armazenamento de dados no cliente

## 📝 Licença

ISC

## 👥 Autor

Elaine M Barros

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📞 Suporte

Para questões ou suporte, abra uma issue no repositório do GitHub.