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

import { ref, reactive } from 'vue';
import { AsgardeoSPAClient, Hooks } from '@asgardeo/auth-spa';
import config from '../config';
import type { AuthState, UseAuthReturn } from '../types/auth';

export interface DerivedState {
  authenticateResponse: any;
  idToken: string[];
  decodedIdTokenHeader: Record<string, string | number | boolean>;
  decodedIDTokenPayload: Record<string, string | number | boolean>;
}

// Create a singleton client instance
let clientInstance: AsgardeoSPAClient | null = null;
let isInitialized = false;

const initializeClient = async () => {
  if (clientInstance && isInitialized) {
    return clientInstance;
  }

  console.log('=== INITIALIZING AsgardeoSPAClient ===');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Config object:', JSON.stringify(config, null, 2));
  
  try {
    console.log('Getting AsgardeoSPAClient instance...');
    // Get the singleton instance
    clientInstance = AsgardeoSPAClient.getInstance();
    console.log('AsgardeoSPAClient instance obtained successfully');
    
    // Register sign-out hooks early
    clientInstance.on(Hooks.SignOut, () => {
      console.log('Sign-out hook triggered during initialization...');
    });
    
    clientInstance.on(Hooks.SignOutFailed, (error) => {
      console.error('Sign-out failed hook triggered during initialization:', error);
    });
    
    // Initialize the client with config
    console.log('Initializing client with config...');
    await clientInstance.initialize(config);
    console.log('Client initialized successfully');
    
    isInitialized = true;
    return clientInstance;
  } catch (error) {
    console.error('Error creating/initializing AsgardeoSPAClient:', error);
    console.error('Error details:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });
    throw error;
  }
};

export function useAuth(): UseAuthReturn {
  console.log('=== INITIALIZING useAuth ===');
  
  const derivedAuthenticationState = ref<DerivedState | null>(null);
  
  const state = reactive<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  const loadUserData = async () => {
    try {
      const client = await initializeClient();
      const basicUserInfo = await client.getBasicUserInfo();
      const idToken = await client.getIDToken();
      const decodedIDToken = await client.getDecodedIDToken();

      const derivedState: DerivedState = {
        authenticateResponse: basicUserInfo,
        idToken: idToken.split("."),
        decodedIdTokenHeader: JSON.parse(atob(idToken.split(".")[0])),
        decodedIDTokenPayload: decodedIDToken
      };

      derivedAuthenticationState.value = derivedState;
    } catch (error) {
      console.error("Error loading user data:", error);
      throw error;
    }
  };

  const signIn = async () => {
    try {
      console.log('=== SIGN IN PROCESS START ===');
      console.log('Step 1: Initializing sign in...');
      console.log('Client config:', JSON.stringify(config, null, 2));
      console.log('Current URL:', window.location.href);
      
      state.isLoading = true;
      state.error = null;
      
      const client = await initializeClient();
      console.log('Step 2: Calling client.signIn()...');
      
      // Check if we're in a callback (redirected back from auth server)
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const sessionState = urlParams.get('session_state');
      const stateParam = urlParams.get('state');
      
      if (code) {
        console.log('Step 3: Processing callback with authorization code...');
        // Call signIn with the authorization code to complete the flow
        const result = await client.signIn({}, code, sessionState || undefined, stateParam || undefined);
        console.log('Step 4: Sign in completed with result:', result);
        
        if (result) {
          await loadUserData();
        }
        return;
      }
      
      console.log('Step 3: Initiating sign in flow...');
      // Start the sign in flow
      const result = await client.signIn();
      console.log('Step 4: Sign in initiated, result:', result);
      
      // The SDK should handle the redirect automatically
      console.log('=== SIGN IN PROCESS END ===');
      
    } catch (error) {
      console.error('=== SIGN IN ERROR ===');
      console.error('Error type:', typeof error);
      console.error('Error constructor:', error.constructor.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      console.error('Full error object:', error);
      console.error('Error keys:', Object.keys(error));
      
      state.error = error;
      throw error;
    } finally {
      state.isLoading = false;
      console.log('Sign in process finished (finally block)');
    }
  };

  const signOut = async () => {
    try {
      console.log('=== SIGN OUT PROCESS START ===');
      console.log('Current URL:', window.location.href);
      console.log('Config:', JSON.stringify(config, null, 2));
      
      state.isLoading = true;
      state.error = null;
      
      const client = await initializeClient();
      console.log('Step 1: Client obtained successfully');
      
      // Check if user is authenticated before logout
      const isAuthenticated = await client.isAuthenticated();
      console.log('Step 2: User authenticated status:', isAuthenticated);
      
      if (!isAuthenticated) {
        console.log('User not authenticated, just redirecting to home...');
        state.isAuthenticated = false;
        derivedAuthenticationState.value = null;
        window.location.href = config.signOutRedirectURL;
        return;
      }
      
      console.log('Step 3: Registering sign-out hooks...');
      
      // Register sign-out hook to clear local session data
      client.on(Hooks.SignOut, () => {
        console.log('Sign-out hook triggered, clearing local session...');
        state.isAuthenticated = false;
        derivedAuthenticationState.value = null;
      });
      
      // Register sign-out-failed hook to handle errors
      client.on(Hooks.SignOutFailed, (error) => {
        console.error('Sign-out failed hook triggered:', error);
        state.error = error;
      });
      
      console.log('Step 4: Calling client.signOut()...');
      
      // Use the SDK's signOut method
      const result = await client.signOut();
      console.log('Step 5: Sign out completed, result:', result);
      
      // Clear local state immediately for better UX
      state.isAuthenticated = false;
      derivedAuthenticationState.value = null;
      
      // The SDK should handle the redirect automatically
      // If we reach here, it means the redirect didn't happen
      console.log('Step 6: Manual redirect to home page...');
      window.location.href = config.signOutRedirectURL;
      
      console.log('=== SIGN OUT PROCESS END ===');
      
    } catch (error) {
      console.error('=== SIGN OUT ERROR ===');
      console.error('Error type:', typeof error);
      console.error('Error constructor:', error.constructor.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      console.error('Full error object:', error);
      console.error('Error keys:', Object.keys(error));
      
      // Fallback: just redirect to home page
      console.log('Attempting fallback redirect to home page...');
      try {
        // Clear local state
        state.isAuthenticated = false;
        derivedAuthenticationState.value = null;
        
        window.location.href = config.signOutRedirectURL;
      } catch (redirectError) {
        console.error('Fallback redirect also failed:', redirectError);
        state.error = error;
        throw error;
      }
    } finally {
      state.isLoading = false;
      console.log('Sign out process finished (finally block)');
    }
  };

  // Initialize authentication state
  const initializeAuth = async () => {
    try {
      state.isLoading = true;
      
      const client = await initializeClient();
      
      // Check if user is authenticated
      const isAuthenticated = await client.isAuthenticated();
      state.isAuthenticated = isAuthenticated;
      
      if (isAuthenticated) {
        await loadUserData();
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      state.error = error;
    } finally {
      state.isLoading = false;
    }
  };

  return {
    state,
    derivedAuthenticationState,
    signIn,
    signOut,
    loadUserData,
    initializeAuth
  };
}
