const { chromium } = require('playwright');

async function debugConsole() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Listen for console messages
  page.on('console', msg => {
    console.log(`Console ${msg.type()}: ${msg.text()}`);
  });
  
  // Listen for page errors
  page.on('pageerror', error => {
    console.log(`Page Error: ${error.message}`);
  });
  
  // Listen for network failures
  page.on('requestfailed', request => {
    console.log(`Request Failed: ${request.url()} - ${request.failure().errorText}`);
  });
  
  try {
    console.log('Loading simulator page...');
    await page.goto('https://syzygyx.github.io/R2-D2/simulator-goldenlayout.html');
    
    console.log('Waiting for page to load...');
    await page.waitForTimeout(5000);
    
    console.log('Checking for Python iframe...');
    const pythonIframe = await page.$('iframe[src*="python.html"]');
    if (pythonIframe) {
      console.log('Python iframe found, checking its console...');
      
      // Get the iframe's frame
      const frame = await pythonIframe.contentFrame();
      if (frame) {
        // Listen to iframe console
        frame.on('console', msg => {
          console.log(`Python Console ${msg.type()}: ${msg.text()}`);
        });
        
        frame.on('pageerror', error => {
          console.log(`Python Page Error: ${error.message}`);
        });
        
        // Wait a bit more for iframe to load
        await page.waitForTimeout(3000);
      }
    }
    
    console.log('Test completed. Check console output above.');
    
  } catch (error) {
    console.log(`Test Error: ${error.message}`);
  } finally {
    await browser.close();
  }
}

debugConsole().catch(console.error);