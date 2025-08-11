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

/**
 * Validates if a string is a valid URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validates if a string is not empty
 */
export const isNotEmpty = (value: string): boolean => {
  return value !== null && value !== undefined && value.trim() !== '';
};

/**
 * Validates if a value is a valid email address
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates if a value is a valid client ID
 */
export const isValidClientId = (clientId: string): boolean => {
  return isNotEmpty(clientId) && clientId !== 'your-client-id' && clientId !== 'your-production-client-id';
};

/**
 * Validates authentication configuration
 */
export const validateAuthConfig = (config: any): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!isValidClientId(config.clientID)) {
    errors.push('Invalid or missing clientID');
  }

  if (!isValidUrl(config.baseUrl)) {
    errors.push('Invalid baseUrl');
  }

  if (!isValidUrl(config.signInRedirectURL)) {
    errors.push('Invalid signInRedirectURL');
  }

  if (!isValidUrl(config.signOutRedirectURL)) {
    errors.push('Invalid signOutRedirectURL');
  }

  if (!Array.isArray(config.scope) || config.scope.length === 0) {
    errors.push('Invalid or empty scope array');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Formats error messages for display
 */
export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (error && typeof error === 'object' && error.message) {
    return error.message;
  }
  
  return 'An unknown error occurred';
};

/**
 * Checks if the current environment is browser
 */
export const isBrowser = (): boolean => {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
};

/**
 * Safely parses JSON with error handling
 */
export const safeJsonParse = (jsonString: string, fallback: any = null): any => {
  try {
    return JSON.parse(jsonString);
  } catch {
    return fallback;
  }
};
