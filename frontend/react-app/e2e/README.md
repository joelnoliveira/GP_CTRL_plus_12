# Testes E2E com Playwright

## Estrutura

```
e2e/
├── login.spec.js          # Testes da página de Login
├── register.spec.js       # Testes da página de Registo
├── auth-flow.spec.js      # Testes de fluxo completo de autenticação
└── helpers/
    └── auth.helpers.js    # Funções auxiliares para testes de auth
```

## Configuração Inicial

### 1. Instalar dependências

```bash
cd frontend/react-app
npm install
```

### 2. Instalar browsers do Playwright

```bash
npx playwright install
```

## Executar Testes

### Todos os testes (headless)
```bash
npm run test:e2e
```

### Testes com interface visual
```bash
npm run test:e2e:ui
```

### Testes com browser visível
```bash
npm run test:e2e:headed
```

### Modo debug
```bash
npm run test:e2e:debug
```

### Ver relatório dos testes
```bash
npm run test:e2e:report
```

### Executar apenas testes de login
```bash
npx playwright test login.spec.js
```

### Executar apenas testes de registo
```bash
npx playwright test register.spec.js
```

## Configuração do reCAPTCHA para Testes

Os formulários de Login e Registo usam reCAPTCHA. Para testes automatizados, existem duas opções:

### Opção 1: Usar Test Keys do Google (Recomendado)

O Google fornece test keys que sempre passam a verificação:

- **Site Key**: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
- **Secret Key**: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`

Configurar no ficheiro `.env.test`:
```
REACT_APP_RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
```

### Opção 2: Mock das respostas do backend

Os helpers em `auth.helpers.js` incluem funções para mockar respostas:

```javascript
const { mockSuccessfulLogin, mockFailedLogin } = require('./helpers/auth.helpers');

test('login com mock', async ({ page }) => {
  await mockSuccessfulLogin(page);
  // ... resto do teste
});
```

## Testes Incluídos

### Login (`login.spec.js`)
- ✅ Carregar página corretamente
- ✅ Validação de email vazio
- ✅ Validação de email inválido
- ✅ Validação de password vazia
- ✅ Validação de password curta (< 8 caracteres)
- ✅ Navegação para página de registo
- ✅ Navegação por teclado
- ✅ Integração com backend (mocked)

### Registo (`register.spec.js`)
- ✅ Carregar página corretamente
- ✅ Validação de email
- ✅ Validação de password
- ✅ Validação de confirmação de password
- ✅ Validação de passwords não coincidentes
- ✅ Navegação por teclado
- ✅ Indicadores de campos obrigatórios

### Fluxo de Autenticação (`auth-flow.spec.js`)
- ✅ Jornada completa de registo → login
- ✅ Navegação entre páginas
- ✅ Casos limite (emails longos, espaços, etc.)
- ✅ Responsividade (mobile, tablet)

## Browsers Testados

Por defeito, os testes correm em:
- Chromium
- Firefox
- WebKit (Safari)

Para testar apenas num browser:
```bash
npx playwright test --project=chromium
```

## Relatórios

Após execução, o relatório HTML está disponível em:
```
playwright-report/index.html
```

Screenshots de falhas são guardados automaticamente.

## CI/CD

Para integração em pipeline CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Install Playwright
  run: npx playwright install --with-deps
  
- name: Run E2E Tests
  run: npm run test:e2e
  
- name: Upload Report
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
```

## Troubleshooting

### Testes falham com timeout
- Verificar se o frontend está a correr em `http://localhost:3001`
- Aumentar timeout em `playwright.config.js`

### reCAPTCHA bloqueia testes
- Usar test keys do Google (ver acima)
- Ou desativar reCAPTCHA em ambiente de teste

### Browser não instala
```bash
npx playwright install --with-deps
```
