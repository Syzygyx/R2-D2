const { test, expect } = require('@playwright/test');

test.describe('SITH R2-D2 Simulator', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the simulator
    await page.goto('/simulator.html');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should load the main simulator page', async ({ page }) => {
    // Check if the page title is correct
    await expect(page).toHaveTitle(/SITH.*Simulator/);
    
    // Check if the header is visible
    await expect(page.locator('h1')).toContainText('SITH Integrated R2-D2 Simulator');
    
    // Check if the subtitle is visible
    await expect(page.locator('p')).toContainText('Python Control + 3D Visualization + Shadow Protocol');
  });

  test('should show loading screen initially', async ({ page }) => {
    // Check if loading screen is visible
    await expect(page.locator('#loadingScreen')).toBeVisible();
    
    // Check if loading text is present
    await expect(page.locator('#loadingText')).toBeVisible();
  });

  test('should load all four components', async ({ page }) => {
    // Wait for loading screen to disappear (max 30 seconds)
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if all four components are loaded
    const components = [
      { name: 'Python Control', selector: 'iframe[src*="python.html"]' },
      { name: '3D Viewer', selector: 'iframe[src*="viewer.html"]' },
      { name: 'Demos', selector: 'iframe[src*="demos.html"]' },
      { name: 'Help', selector: 'iframe[src*="help.html"]' }
    ];

    for (const component of components) {
      await expect(page.locator(component.selector)).toBeVisible();
    }
  });

  test('should have resizable panels', async ({ page }) => {
    // Wait for layout to load
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if GoldenLayout is initialized
    await expect(page.locator('.lm_goldenlayout')).toBeVisible();
    
    // Check if splitters are present (indicating resizable panels)
    await expect(page.locator('.lm_splitter')).toHaveCount(3); // 2 columns + 1 row splitter
  });

  test('should have proper Sith theming', async ({ page }) => {
    // Wait for layout to load
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if the main container has the Sith theme
    const body = page.locator('body');
    await expect(body).toHaveCSS('background', /radial-gradient/);
    await expect(body).toHaveCSS('color', 'rgb(255, 0, 0)');
    
    // Check if header has proper styling
    const header = page.locator('.header');
    await expect(header).toHaveCSS('background', /linear-gradient/);
    await expect(header).toHaveCSS('border-bottom-color', 'rgb(255, 0, 0)');
  });

  test('should handle mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Wait for layout to load
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if the layout adapts to mobile
    await expect(page.locator('.lm_goldenlayout')).toBeVisible();
    
    // Check if header text is smaller on mobile
    const headerH1 = page.locator('.header h1');
    const fontSize = await headerH1.evaluate(el => getComputedStyle(el).fontSize);
    expect(parseFloat(fontSize)).toBeLessThan(32); // Should be smaller than desktop
  });

  test('should load individual component pages', async ({ page }) => {
    const components = [
      { url: '/python.html', title: 'Python Control' },
      { url: '/viewer.html', title: '3D Viewer' },
      { url: '/demos.html', title: 'Demos' },
      { url: '/help.html', title: 'Help' }
    ];

    for (const component of components) {
      await page.goto(component.url);
      await page.waitForLoadState('networkidle');
      
      // Check if page loads without errors
      await expect(page.locator('body')).toBeVisible();
      
      // Check if the component-specific content is present
      await expect(page.locator('h2')).toContainText(component.title);
    }
  });

  test('should handle Python component loading', async ({ page }) => {
    await page.goto('/python.html');
    await page.waitForLoadState('networkidle');
    
    // Check if Python-specific elements are present
    await expect(page.locator('#codeEditor')).toBeVisible();
    await expect(page.locator('#outputConsole')).toBeVisible();
    await expect(page.locator('#runBtn')).toBeVisible();
    await expect(page.locator('#clearBtn')).toBeVisible();
    
    // Check if Pyodide loading is initiated
    await expect(page.locator('#loading')).toBeVisible();
  });

  test('should handle 3D Viewer component loading', async ({ page }) => {
    await page.goto('/viewer.html');
    await page.waitForLoadState('networkidle');
    
    // Check if 3D viewer elements are present
    await expect(page.locator('#viewerContainer')).toBeVisible();
    await expect(page.locator('button[onclick="resetCamera()"]')).toBeVisible();
    await expect(page.locator('button[onclick="toggleWireframe()"]')).toBeVisible();
    
    // Check if Three.js is loading
    await expect(page.locator('#loading3D')).toBeVisible();
  });

  test('should handle Demos component loading', async ({ page }) => {
    await page.goto('/demos.html');
    await page.waitForLoadState('networkidle');
    
    // Check if demo elements are present
    await expect(page.locator('.demo-btn')).toHaveCount(6); // 6 demo buttons
    await expect(page.locator('.quick-btn')).toHaveCount(8); // 8 quick action buttons
    
    // Check if demo buttons are clickable
    const basicDemo = page.locator('button[onclick="loadExample(\'basic\')"]');
    await expect(basicDemo).toBeVisible();
    await expect(basicDemo).toBeEnabled();
  });

  test('should handle Help component loading', async ({ page }) => {
    await page.goto('/help.html');
    await page.waitForLoadState('networkidle');
    
    // Check if help content is present
    await expect(page.locator('.help-section')).toHaveCount(6); // 6 help sections
    await expect(page.locator('.command-list')).toBeVisible();
    
    // Check if command reference is present
    await expect(page.locator('.command-code')).toContainText(':OP01');
    await expect(page.locator('.command-code')).toContainText(':CL01');
    await expect(page.locator('.command-code')).toContainText(':SEwave');
  });

  test('should handle cross-component communication', async ({ page }) => {
    // Wait for simulator to load
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if message handling is set up
    const messageHandlers = await page.evaluate(() => {
      return window.simulator && window.simulator.setupMessageHandlers;
    });
    expect(messageHandlers).toBeDefined();
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Navigate to a non-existent page
    await page.goto('/nonexistent.html');
    
    // Should get 404
    await expect(page.locator('body')).toContainText('404');
  });

  test('should have proper accessibility', async ({ page }) => {
    await page.goto('/simulator.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    
    // Check if buttons have proper labels
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      expect(text).toBeTruthy(); // Buttons should have text content
    }
  });

  test('should handle network errors', async ({ page }) => {
    // Block network requests to simulate offline
    await page.route('**/*', route => route.abort());
    
    await page.goto('/simulator.html');
    
    // Should show loading screen and eventually error
    await expect(page.locator('#loadingScreen')).toBeVisible();
    
    // Wait for error message
    await expect(page.locator('#loadingText')).toContainText('Error');
  });
});