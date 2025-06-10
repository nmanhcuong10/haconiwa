#!/usr/bin/env node

/**
 * Pre-publish check script for haconiwa npm package
 * Ensures Python and haconiwa are available before publishing
 */

const { checkHaconiwaInstallation } = require('./bin/haconiwa');

function main() {
  console.log('🔍 Checking Python and haconiwa installation...\n');
  
  const installationType = checkHaconiwaInstallation();
  
  if (!installationType) {
    console.error('❌ Pre-publish check failed!');
    console.error('');
    console.error('Haconiwa Python package is not available.');
    console.error('Please ensure haconiwa is installed via pip:');
    console.error('');
    console.error('  pip install haconiwa --upgrade');
    console.error('');
    console.error('This npm package is a wrapper for the Python haconiwa package.');
    console.error('The Python package must be available for testing.');
    console.error('');
    process.exit(1);
  }
  
  console.log('✅ Python haconiwa package is available!');
  console.log(`📦 Installation type: ${installationType}`);
  console.log('');
  console.log('🚀 Ready to publish npm package.');
  console.log('');
  console.log('Note: Users will need to install the Python package separately:');
  console.log('  pip install haconiwa');
  console.log('');
}

if (require.main === module) {
  main();
} 