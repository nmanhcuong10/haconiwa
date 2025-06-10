/**
 * Haconiwa - AI Collaborative Development Support CLI Tool
 * 
 * This is an npm wrapper for the Python haconiwa package.
 * It provides easy access to haconiwa commands from Node.js environments.
 * 
 * @author Daisuke Motoki <kanri@kandaquantum.co.jp>
 * @license MIT
 */

const spawn = require('cross-spawn');
const { checkHaconiwaInstallation } = require('./bin/haconiwa');

/**
 * Execute haconiwa command programmatically
 * @param {string[]} args - Command arguments
 * @param {object} options - Spawn options
 * @returns {Promise<object>} - Command result
 */
function exec(args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const installationType = checkHaconiwaInstallation();
    
    if (!installationType) {
      reject(new Error('Haconiwa Python package is not installed. Please run: pip install haconiwa'));
      return;
    }
    
    let command;
    let cmdArgs;
    
    if (installationType === 'python-module') {
      command = 'python';
      cmdArgs = ['-m', 'haconiwa'].concat(args);
    } else if (installationType === 'python3-module') {
      command = 'python3';
      cmdArgs = ['-m', 'haconiwa'].concat(args);
    } else {
      command = 'haconiwa';
      cmdArgs = args;
    }
    
    const defaultOptions = {
      stdio: 'pipe',
      shell: false
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    const child = spawn(command, cmdArgs, finalOptions);
    
    let stdout = '';
    let stderr = '';
    
    if (child.stdout) {
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
    }
    
    if (child.stderr) {
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
    }
    
    child.on('exit', (code, signal) => {
      resolve({
        code,
        signal,
        stdout,
        stderr,
        success: code === 0
      });
    });
    
    child.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Check if haconiwa is available
 * @returns {boolean|string} - Installation type or false if not available
 */
function isAvailable() {
  return checkHaconiwaInstallation();
}

/**
 * Get haconiwa version
 * @returns {Promise<string>} - Version string
 */
async function getVersion() {
  try {
    const result = await exec(['--version']);
    if (result.success) {
      return result.stdout.trim();
    }
    throw new Error('Failed to get version');
  } catch (error) {
    throw new Error(`Failed to get haconiwa version: ${error.message}`);
  }
}

/**
 * Common commands shortcuts
 */
const commands = {
  /**
   * Apply YAML configuration
   * @param {string} file - YAML file path
   * @param {object} options - Additional options
   */
  async apply(file, options = {}) {
    const args = ['apply', '-f', file];
    if (options.forceClone) args.push('--force-clone');
    if (options.attach) args.push('--attach');
    if (options.noAttach) args.push('--no-attach');
    return exec(args, options.spawnOptions);
  },
  
  /**
   * List spaces
   * @param {object} options - Additional options
   */
  async listSpaces(options = {}) {
    return exec(['space', 'list'], options.spawnOptions);
  },
  
  /**
   * Build company
   * @param {string} name - Company name
   * @param {object} options - Additional options
   */
  async buildCompany(name, options = {}) {
    const args = ['company', 'build', '--name', name];
    if (options.basePath) args.push('--base-path', options.basePath);
    if (options.noAttach) args.push('--no-attach');
    if (options.rebuild) args.push('--rebuild');
    return exec(args, options.spawnOptions);
  },
  
  /**
   * Delete space
   * @param {string} company - Company name
   * @param {object} options - Additional options
   */
  async deleteSpace(company, options = {}) {
    const args = ['space', 'delete', '-c', company];
    if (options.cleanDirs) args.push('--clean-dirs');
    if (options.force) args.push('--force');
    return exec(args, options.spawnOptions);
  }
};

module.exports = {
  exec,
  isAvailable,
  getVersion,
  commands,
  
  // Export version and package info
  version: require('./package.json').version,
  name: 'haconiwa'
}; 