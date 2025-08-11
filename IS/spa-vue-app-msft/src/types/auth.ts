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

// Authentication state interface
export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;
}

// User information interface
export interface UserInfo {
  sub: string;
  name?: string;
  given_name?: string;
  family_name?: string;
  email?: string;
  email_verified?: boolean;
  picture?: string;
  [key: string]: any;
}

// ID Token interface
export interface IDToken {
  header: Record<string, any>;
  payload: Record<string, any>;
  signature: string;
}

// Authentication response interface
export interface AuthResponse {
  userInfo: UserInfo;
  idToken: IDToken;
  accessToken?: string;
  refreshToken?: string;
}

// Authentication error interface
export interface AuthError {
  code: string;
  message: string;
  details?: any;
}

// Authentication configuration interface
export interface AuthConfig {
  clientID: string;
  baseUrl: string;
  signInRedirectURL: string;
  signOutRedirectURL: string;
  scope: string[];
  enableOIDCSessionManagement: boolean;
  checkSessionInterval: number;
  environment: string;
}

// Authentication hooks interface
export interface AuthHooks {
  onSignIn?: (response: AuthResponse) => void;
  onSignOut?: () => void;
  onError?: (error: AuthError) => void;
}

// Authentication methods interface
export interface AuthMethods {
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
  loadUserData: () => Promise<void>;
  initializeAuth: () => Promise<void>;
}

// Authentication composable return interface
export interface UseAuthReturn {
  state: AuthState;
  derivedAuthenticationState: any;
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
  loadUserData: () => Promise<void>;
  initializeAuth: () => Promise<void>;
}
