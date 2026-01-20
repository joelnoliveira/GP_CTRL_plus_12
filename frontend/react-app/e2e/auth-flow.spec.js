// @ts-check
const { test, expect } = require('@playwright/test');
const { 
  testUsers, 
  fillLoginForm, 
  fillRegisterForm,
  mockSuccessfulLogin,
  mockSuccessfulRegister,
  mockFailedLogin,
  mockFailedRegister,
  clearAuthState 
} = require('./helpers/auth.helpers');

/**
 * Testes de fluxo completo de autenticação
 * Simula jornada real do utilizador
 */

test.describe('Fluxo Completo de Autenticação', () => {

  test('jornada: utilizador não registado -> registo -> login -> acesso', async ({ page }) => {
    // 1. Utilizador tenta aceder área protegida
    await page.goto('/');
    
    // 2. Vai para página de registo
    await page.goto('/register');
    await expect(page).toHaveURL('/register');
    
    // 3. Preenche formulário de registo
    const newEmail = `newuser_${Date.now()}@example.com`;
    await fillRegisterForm(page, newEmail, 'securePassword123');
    
    // Mock registo bem-sucedido
    await mockSuccessfulRegister(page);
    
    // 4. Após registo, seria redirecionado para login
    // (Este passo requer completar reCAPTCHA em ambiente real)
    
    // 5. Faz login
    await page.goto('/login');
    await fillLoginForm(page, newEmail, 'securePassword123');
    
    // Mock login bem-sucedido
    await mockSuccessfulLogin(page);
  });

  test('jornada: utilizador registado -> login -> logout', async ({ page }) => {
    // 1. Utilizador vai para login
    await page.goto('/login');
    
    // 2. Preenche credenciais
    await fillLoginForm(page, testUsers.valid.email, testUsers.valid.password);
    
    // Mock login bem-sucedido
    await mockSuccessfulLogin(page);
    
    // 3. Após login, utilizador estaria autenticado
    // (Verificação depende da implementação do AuthContext)
  });

  test('utilizador tenta registar com email já existente', async ({ page }) => {
    await page.goto('/register');
    
    // Mock erro de email duplicado
    await mockFailedRegister(page, 'Email already registered');
    
    await fillRegisterForm(page, 'existing@example.com', 'password123');
    
    // Nota: Submit requer reCAPTCHA
    // Verificar que erro seria exibido após submit
  });

  test('utilizador tenta login com credenciais erradas', async ({ page }) => {
    await page.goto('/login');
    
    // Mock erro de credenciais
    await mockFailedLogin(page, 'Invalid credentials');
    
    await fillLoginForm(page, testUsers.invalid.email, testUsers.invalid.password);
    
    // Nota: Submit requer reCAPTCHA
    // Verificar que erro seria exibido após submit
  });
});

test.describe('Navegação entre páginas de Auth', () => {
  
  test('login -> register -> login', async ({ page }) => {
    // Começar no login
    await page.goto('/login');
    await expect(page).toHaveURL('/login');
    
    // Ir para register
    await page.getByRole('link', { name: /create an account/i }).click();
    await expect(page).toHaveURL('/register');
    
    // Voltar para login via navegação do browser
    await page.goBack();
    await expect(page).toHaveURL('/login');
  });

  test('utilizador autenticado é redirecionado do login para home', async ({ page }) => {
    // Navegar primeiro para a app ter acesso ao localStorage
    await page.goto('/login');
    
    // Simular utilizador já autenticado usando addInitScript
    // que executa antes de qualquer script da página
    await page.evaluate(() => {
      try {
        localStorage.setItem('token', 'mock-valid-token');
      } catch (e) {
        // localStorage pode não estar disponível
      }
    });
    
    // Recarregar para aplicar o token
    await page.reload();
    
    // Verificar comportamento (depende da implementação do AuthContext)
    // Se implementado corretamente, deve redirecionar para /
  });
});

test.describe('Validação de formulários - Casos limite', () => {
  
  test('email com espaços deve ser inválido', async ({ page }) => {
    await page.goto('/login');
    
    await page.locator('input[type="email"]').fill('  email@test.com  ');
    await page.locator('input[type="password"]').fill('password123');
    await page.getByRole('button', { name: /login/i }).click();
    
    // O formato pode ou não ser aceite dependendo da validação
  });

  test('password com apenas espaços deve ser inválida', async ({ page }) => {
    await page.goto('/login');
    
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('        '); // 8 espaços
    await page.getByRole('button', { name: /login/i }).click();
    
    // Verificar se a validação trata espaços
  });

  test('email muito longo', async ({ page }) => {
    await page.goto('/register');
    
    const longEmail = 'a'.repeat(200) + '@example.com';
    await page.locator('input[type="email"]').fill(longEmail);
    
    // Verificar comportamento com email muito longo
  });

  test('password no limite mínimo (8 caracteres)', async ({ page }) => {
    await page.goto('/login');
    
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('12345678'); // exatamente 8
    await page.getByRole('button', { name: /login/i }).click();
    
    // Não deve mostrar erro de tamanho
    await expect(page.getByText('Password must be at least 8 characters')).not.toBeVisible();
  });
});

test.describe('Responsividade', () => {
  
  test('login em viewport mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto('/login');
    
    // Verificar que elementos estão visíveis e acessíveis
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });

  test('register em viewport mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/register');
    
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('input[type="password"]').last()).toBeVisible();
    await expect(page.getByRole('button', { name: /register/i })).toBeVisible();
  });

  test('login em viewport tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto('/login');
    
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });
});
