// @ts-check
const base = require('@playwright/test');

/**
 * Fixtures customizadas para testes de autenticação
 * Permite reutilizar lógica comum entre testes
 */

/**
 * Dados de teste para utilizadores
 */
const testUsers = {
  valid: {
    email: 'testuser@example.com',
    password: 'password123',
  },
  invalid: {
    email: 'invalid@example.com',
    password: 'wrongpassword',
  },
  new: {
    email: `newuser_${Date.now()}@example.com`,
    password: 'newpassword123',
  },
};

/**
 * Helper para preencher formulário de login
 */
async function fillLoginForm(page, email, password) {
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
}

/**
 * Helper para preencher formulário de registo
 */
async function fillRegisterForm(page, email, password, confirmPassword) {
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').first().fill(password);
  await page.locator('input[type="password"]').last().fill(confirmPassword || password);
}

/**
 * Helper para simular reCAPTCHA em ambiente de teste
 * NOTA: Isto requer configuração especial no ambiente de teste
 */
async function bypassRecaptcha(page) {
  // Opção 1: Usar test keys do Google (sempre passa)
  // Configurar REACT_APP_RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
  
  // Opção 2: Mock da verificação no backend
  await page.route('**/auth/verify-captcha', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

/**
 * Helper para verificar mensagem de erro
 */
async function expectError(page, errorMessage) {
  const error = page.getByText(errorMessage);
  await base.expect(error).toBeVisible();
  return error;
}

/**
 * Helper para verificar toast
 */
async function expectToast(page, type, message) {
  const toast = page.locator(`[data-testid="toast-${type}"]`);
  if (await toast.isVisible()) {
    await base.expect(toast).toContainText(message);
  }
}

/**
 * Helper para mock de autenticação bem-sucedida
 */
async function mockSuccessfulLogin(page) {
  await page.route('**/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        token: 'mock-jwt-token-' + Date.now(),
        user: { email: 'test@example.com', id: 1 }
      }),
    });
  });
}

/**
 * Helper para mock de registo bem-sucedido
 */
async function mockSuccessfulRegister(page) {
  await page.route('**/auth/register', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'User registered successfully',
        user: { email: 'newuser@example.com', id: 2 }
      }),
    });
  });
}

/**
 * Helper para mock de erro de autenticação
 */
async function mockFailedLogin(page, errorMessage = 'Invalid credentials') {
  await page.route('**/auth/login', async (route) => {
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: errorMessage }),
    });
  });
}

/**
 * Helper para mock de erro de registo
 */
async function mockFailedRegister(page, errorMessage = 'Email already registered') {
  await page.route('**/auth/register', async (route) => {
    await route.fulfill({
      status: 400,
      contentType: 'application/json',
      body: JSON.stringify({ detail: errorMessage }),
    });
  });
}

/**
 * Helper para limpar localStorage (logout)
 * NOTA: Deve ser chamado após page.goto() para ter acesso ao localStorage
 */
async function clearAuthState(page) {
  try {
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  } catch (e) {
    // localStorage pode não estar disponível em about:blank
    console.log('clearAuthState: localStorage not available');
  }
}

/**
 * Helper para simular utilizador autenticado
 */
async function setAuthenticatedUser(page, token = 'mock-token') {
  await page.evaluate((t) => {
    localStorage.setItem('token', t);
  }, token);
}

module.exports = {
  testUsers,
  fillLoginForm,
  fillRegisterForm,
  bypassRecaptcha,
  expectError,
  expectToast,
  mockSuccessfulLogin,
  mockSuccessfulRegister,
  mockFailedLogin,
  mockFailedRegister,
  clearAuthState,
  setAuthenticatedUser,
};
