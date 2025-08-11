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

export const USER_DENIED_LOGOUT = "User denied the logout request";

// Authentication error messages
export const AUTH_ERROR_MESSAGES = {
  OAUTH_PROCESSING_FAILED: 'Logout error: OAuth processing failed. Please try again.',
  FAILED_TO_LOAD_USER_DATA: 'Failed to load user data',
  NO_AUTHORIZATION_CODE: 'No authorization code found in URL',
  AUTHENTICATION_ERROR: 'Authentication error',
  LOGOUT_ERROR: 'Logout error',
  UNKNOWN_ERROR: 'Unknown error occurred',
  LOGIN_FAILED: 'Login failed'
} as const;

// URL constants
export const URL_CONSTANTS = {
  HOME: '/',
  AUTH_CALLBACK: '/auth/callback'
} as const;

// Loading messages
export const LOADING_MESSAGES = {
  PROCESSING_AUTH: 'Processing authentication...',
  PROCESSING_AUTH_DESCRIPTION: 'Please wait while we process your authentication response.',
  LOGGING_OUT: 'Logging out...',
  LOGOUT: 'Logout'
} as const;

// UI text constants
export const UI_TEXT = {
  AUTHENTICATION_RESPONSE: 'Authentication Response',
  USER_INFORMATION: 'User Information',
  ID_TOKEN: 'ID Token',
  ENCODED: 'Encoded',
  DECODED: 'Decoded',
  HEADER: 'Header',
  PAYLOAD: 'Payload',
  SIGNATURE: 'Signature',
  GO_BACK_TO_HOME: 'Go Back to Home',
  TRY_AGAIN: 'Try Again'
} as const;
