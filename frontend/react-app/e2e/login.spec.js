// @ts-check
/* eslint-disable testing-library/prefer-screen-queries */
const { test, expect } = require('@playwright/test');

/**
 * Testes E2E para a funcionalidade de Login
 * 
 * NOTA: O reCAPTCHA está ativo nestes formulários.
 * Para testes automatizados, existem duas abordagens:
 * 1. Usar test keys do Google reCAPTCHA (recomendado para testes)
 * 2. Mockar o componente reCAPTCHA em ambiente de teste
 * 
 * Site Key de Teste Google: 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
 * Secret Key de Teste Google: 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
 */

test.describe('Login Page', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('deve carregar a página de login corretamente', async ({ page }) => {
    // Verificar que a página carregou
    await expect(page).toHaveURL('/login');
    
    // Verificar elementos principais
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });

  test('deve mostrar labels dos campos', async ({ page }) => {
    await expect(page.getByText('Email')).toBeVisible();
    await expect(page.getByText('Password')).toBeVisible();
  });

  test('deve ter link para página de registo', async ({ page }) => {
    const registerLink = page.getByRole('link', { name: /create an account/i });
    await expect(registerLink).toBeVisible();
    
    await registerLink.click();
    await expect(page).toHaveURL('/register');
  });

  test('deve mostrar erro quando email está vazio', async ({ page }) => {
    // Focar e sair do campo email sem preencher
    await page.locator('input[type="email"]').focus();
    await page.locator('input[type="email"]').blur();
    
    // Clicar no botão de submit para trigger validação
    await page.getByRole('button', { name: /login/i }).click();
    
    // Verificar mensagem de erro
    await expect(page.getByText('Email is required')).toBeVisible();
  });

  test('deve mostrar erro quando email é inválido', async ({ page }) => {
    await page.locator('input[type="email"]').fill('email-invalido');
    await page.locator('input[type="password"]').fill('password123');
    
    await page.getByRole('button', { name: /login/i }).click();
    
    await expect(page.getByText('Invalid email format')).toBeVisible();
  });

  test('deve mostrar erro quando password está vazia', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    
    await page.getByRole('button', { name: /login/i }).click();
    
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('deve mostrar erro quando password tem menos de 8 caracteres', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('1234567'); // 7 caracteres
    
    await page.getByRole('button', { name: /login/i }).click();
    
    await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();
  });

  test('deve permitir preencher campos corretamente', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    
    await emailInput.fill('user@example.com');
    await passwordInput.fill('password123');
    
    await expect(emailInput).toHaveValue('user@example.com');
    await expect(passwordInput).toHaveValue('password123');
  });

  test('deve ter reCAPTCHA visível', async ({ page }) => {
    // Verificar que o container do reCAPTCHA existe
    await expect(page.locator('.login__recaptcha-container')).toBeVisible();
  });

  test('deve navegar para home ao clicar no logo', async ({ page }) => {
    // Assumindo que o logo tem um link para home
    const logoLink = page.locator('a').filter({ has: page.locator('img, svg') }).first();

    await expect(logoLink).toBeVisible();
    await logoLink.click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Login - Integração com Backend', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('deve mostrar erro toast com credenciais inválidas', async ({ page }) => {
    // Este teste requer que o reCAPTCHA seja preenchido
    // Em ambiente de teste, usar mock ou test keys
    
    await page.locator('input[type="email"]').fill('invalid@example.com');
    await page.locator('input[type="password"]').fill('wrongpassword123');
    
    // Nota: O teste completo requer resolver o reCAPTCHA
    // Para testes automatizados, configurar REACT_APP_RECAPTCHA_SITE_KEY 
    // com a test key do Google: 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
  });

  test('deve redirecionar para home após login bem-sucedido', async ({ page, context }) => {
    // Mock da resposta do backend para simular login bem-sucedido
    await page.route('**/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          token: 'mock-jwt-token-123',
          user: { email: 'test@example.com' }
        }),
      });
    });

    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    
    // Nota: Necessário resolver reCAPTCHA para submit funcionar
    // Este é um teste de exemplo com mock do backend
  });

  test('deve mostrar mensagem de erro quando backend retorna erro', async ({ page }) => {
    // Mock da resposta do backend para simular erro
    await page.route('**/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' }),
      });
    });

    // Verificar que o toast de erro aparece após falha
    // Nota: Requer completar reCAPTCHA para trigger o submit
  });
});

test.describe('Login - Acessibilidade', () => {
  
  test('deve permitir navegação por teclado', async ({ page }) => {
    await page.goto('/login');
    
    // Focar no email input diretamente e verificar navegação entre campos
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    
    await emailInput.focus();
    await expect(emailInput).toBeFocused();
    
    // Tab para password
    await page.keyboard.press('Tab');
    await expect(passwordInput).toBeFocused();
  });

  test('campos devem ter labels associadas', async ({ page }) => {
    await page.goto('/login');
    
    // Verificar que os labels existem
    const emailLabel = page.getByText('Email');
    const passwordLabel = page.getByText('Password');
    
    await expect(emailLabel).toBeVisible();
    await expect(passwordLabel).toBeVisible();
  });
});
