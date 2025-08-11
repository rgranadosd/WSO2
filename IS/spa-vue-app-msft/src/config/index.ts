/**
 * Copyright (c) 2021, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
 *
 * WSO2 Inc. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import jsonConfig from '../config.json';
import { validateAuthConfig, isValidUrl } from '../utils/validation';

// Environment detection - single production environment with all features enabled
const isDevelopment = false; // No development environment
const isProduction = true; // Only production environment

// Helper function to safely get environment variables
// Works in both Node.js and browser environments
const getEnvVar = (key: string, defaultValue: string): string => {
  try {
    // Check if we're in a Node.js environment
    if (typeof process !== 'undefined' && process.env && process.env[key]) {
      return process.env[key];
    }
    
    // Check if we're in a browser environment with webpack DefinePlugin
    // Webpack can inject these at build time
    if (typeof window !== 'undefined' && (window as any)[key]) {
      return (window as any)[key];
    }
    
    return defaultValue;
  } catch (error) {
    // If any error occurs, return the default value
    return defaultValue;
  }
};

// Configuration interface
export interface AppConfig {
  clientID: string;
  baseUrl: string;
  signInRedirectURL: string;
  signOutRedirectURL: string;
  scope: string[];
  enableOIDCSessionManagement: boolean;
  checkSessionInterval: number;
  environment: string;
  enableDebugMode: boolean;
  enableHotReload: boolean;
  enableErrorBoundary: boolean;
  enableTypeChecking: boolean;
}

// Merge configuration from JSON file with environment variables
// Environment variables take precedence over JSON config
const config: AppConfig = {
  ...jsonConfig,
  // Override with environment variables if they exist
  clientID: getEnvVar('VUE_APP_CLIENT_ID', jsonConfig.clientID),
  baseUrl: getEnvVar('VUE_APP_BASE_URL', jsonConfig.baseUrl),
  signInRedirectURL: getEnvVar('VUE_APP_SIGN_IN_REDIRECT_URL', jsonConfig.signInRedirectURL),
  signOutRedirectURL: getEnvVar('VUE_APP_SIGN_OUT_REDIRECT_URL', jsonConfig.signOutRedirectURL),
  environment: 'production' // Always production
};

// Validate required configuration
const validateConfig = (config: AppConfig): void => {
  const validation = validateAuthConfig(config);
  
  if (!validation.isValid) {
    throw new Error(`Configuration validation failed: ${validation.errors.join(', ')}`);
  }
  
  // Log configuration status
  if (config.enableDebugMode) {
    console.log('Configuration loaded:', {
      environment: config.environment,
      oidcSessionManagement: config.enableOIDCSessionManagement,
      debugMode: config.enableDebugMode,
      hotReload: config.enableHotReload,
      errorBoundary: config.enableErrorBoundary,
      typeChecking: config.enableTypeChecking
    });
  }
};

// Validate configuration on import
validateConfig(config);

// Export the validated configuration
export default config;

// Export environment info
export const environment = {
  isDevelopment,
  isProduction,
  nodeEnv: 'production'
};
