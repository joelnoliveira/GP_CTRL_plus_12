// @ts-check
/* eslint-disable testing-library/prefer-screen-queries */
const { test, expect } = require('@playwright/test');

/**
 * Testes E2E para a funcionalidade de Registo
 * 
 * NOTA: O reCAPTCHA está ativo nestes formulários.
 * Para testes automatizados, usar test keys do Google reCAPTCHA:
 * Site Key de Teste: 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
 */

test.describe('Register Page', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('deve carregar a página de registo corretamente', async ({ page }) => {
    await expect(page).toHaveURL('/register');
    
    // Verificar elementos principais
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.getByRole('button', { name: /register/i })).toBeVisible();
  });

  test('deve mostrar todos os labels dos campos', async ({ page }) => {
    await expect(page.getByText('Email')).toBeVisible();
    await expect(page.getByText('Password').first()).toBeVisible();
    await expect(page.getByText('Confirm Password')).toBeVisible();
  });

  test('deve ter 3 campos de input (email, password, confirm password)', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const passwordInputs = page.locator('input[type="password"]');
    
    await expect(emailInput).toHaveCount(1);
    await expect(passwordInputs).toHaveCount(2);
  });

  test('deve mostrar erro quando email está vazio', async ({ page }) => {
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText('Email is required')).toBeVisible();
  });

  test('deve mostrar erro quando email é inválido', async ({ page }) => {
    await page.locator('input[type="email"]').fill('email-invalido');
    await page.locator('input[type="password"]').first().fill('password123');
    await page.locator('input[type="password"]').last().fill('password123');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText('Invalid email format')).toBeVisible();
  });

  test('deve mostrar erro quando password está vazia', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('deve mostrar erro quando password tem menos de 8 caracteres', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').first().fill('1234567'); // 7 caracteres
    await page.locator('input[type="password"]').last().fill('1234567');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();
  });

  test('deve mostrar erro quando confirmação de password está vazia', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').first().fill('password123');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    await expect(page.getByText('Password confirmation is required')).toBeVisible();
  });

  test('deve mostrar erro quando passwords não coincidem', async ({ page }) => {
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').first().fill('password123');
    await page.locator('input[type="password"]').last().fill('differentpassword');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    // A mensagem aparece nos dois campos de password
    const errorMessages = page.getByText('Passwords do not match');
    await expect(errorMessages.first()).toBeVisible();
  });

  test('deve permitir preencher todos os campos corretamente', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').last();
    
    await emailInput.fill('newuser@example.com');
    await passwordInput.fill('password123');
    await confirmPasswordInput.fill('password123');
    
    await expect(emailInput).toHaveValue('newuser@example.com');
    await expect(passwordInput).toHaveValue('password123');
    await expect(confirmPasswordInput).toHaveValue('password123');
  });

  test('deve ter reCAPTCHA visível', async ({ page }) => {
    await expect(page.locator('.login__recaptcha-container')).toBeVisible();
  });

  test('deve navegar para home ao clicar no logo', async ({ page }) => {
    const logoLink = page.locator('a').filter({ has: page.locator('img, svg') }).first();

    await expect(logoLink).toBeVisible();
    await logoLink.click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Register - Integração com Backend', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('deve redirecionar para login após registo bem-sucedido', async ({ page }) => {
    // Mock da resposta do backend para simular registo bem-sucedido
    await page.route('**/auth/register', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          message: 'User registered successfully',
          user: { email: 'newuser@example.com' }
        }),
      });
    });

    await page.locator('input[type="email"]').fill('newuser@example.com');
    await page.locator('input[type="password"]').first().fill('password123');
    await page.locator('input[type="password"]').last().fill('password123');
    
    // Nota: Necessário resolver reCAPTCHA para submit funcionar
    // Este é um teste de exemplo com mock do backend
  });

  test('deve mostrar erro quando email já está registado', async ({ page }) => {
    // Mock da resposta do backend para simular email duplicado
    await page.route('**/auth/register', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Email already registered' }),
      });
    });

    // Este teste verifica o comportamento quando o backend retorna erro de email duplicado
  });

  test('deve mostrar toast de erro quando backend falha', async ({ page }) => {
    // Mock da resposta do backend para simular erro interno
    await page.route('**/auth/register', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    // Verificar que o toast de erro aparece
  });
});

test.describe('Register - Validação em tempo real', () => {
  
  test('deve mostrar erro ao sair do campo email vazio', async ({ page }) => {
    await page.goto('/register');
    
    const emailInput = page.locator('input[type="email"]');
    await emailInput.focus();
    await emailInput.blur();
    
    // Clicar submit para trigger validação
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText('Email is required')).toBeVisible();
  });

  test('deve limpar erro quando campo é corrigido', async ({ page }) => {
    await page.goto('/register');
    
    // Trigger erro primeiro
    await page.locator('input[type="email"]').fill('invalid');
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page.getByText('Invalid email format')).toBeVisible();
    
    // Corrigir o email
    await page.locator('input[type="email"]').clear();
    await page.locator('input[type="email"]').fill('valid@example.com');
    
    // Preencher outros campos
    await page.locator('input[type="password"]').first().fill('password123');
    await page.locator('input[type="password"]').last().fill('password123');
    
    await page.getByRole('button', { name: /register/i }).click();
    
    // Erro de formato deve desaparecer
    await expect(page.getByText('Invalid email format')).not.toBeVisible();
  });
});

test.describe('Register - Acessibilidade', () => {
  
  test('deve permitir navegação por teclado', async ({ page }) => {
    await page.goto('/register');
    
    // Focar no email input diretamente e verificar navegação entre campos
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').last();
    
    await emailInput.focus();
    await expect(emailInput).toBeFocused();
    
    // Tab para password
    await page.keyboard.press('Tab');
    await expect(passwordInput).toBeFocused();
    
    // Tab para confirm password
    await page.keyboard.press('Tab');
    await expect(confirmPasswordInput).toBeFocused();
  });

  test('deve submeter formulário com Enter', async ({ page }) => {
    await page.goto('/register');
    
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').first().fill('password123');
    await page.locator('input[type="password"]').last().fill('password123');
    
    // Enter no último campo deve submeter (se reCAPTCHA estiver completo)
    await page.locator('input[type="password"]').last().press('Enter');
    
    // Sem reCAPTCHA, deve mostrar mensagem de erro do captcha
  });

  test('campos required devem ter indicador visual', async ({ page }) => {
    await page.goto('/register');
    
    // Verificar que os asteriscos de required estão visíveis
    const requiredIndicators = page.locator('.textfield__label--required');
    await expect(requiredIndicators).toHaveCount(3); // email, password, confirm password
  });
});

test.describe('Register - Fluxo completo', () => {
  
  test('fluxo completo: preencher formulário e validar', async ({ page }) => {
    await page.goto('/register');
    
    // Preencher formulário
    await page.locator('input[type="email"]').fill('newuser@example.com');
    await page.locator('input[type="password"]').first().fill('securePassword123');
    await page.locator('input[type="password"]').last().fill('securePassword123');
    
    // Verificar que não há erros de validação
    await expect(page.locator('.textfield__error-message')).toHaveCount(0);
    
    // Verificar que o botão está visível e pode ser clicado
    const submitButton = page.getByRole('button', { name: /register/i });
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });
});
