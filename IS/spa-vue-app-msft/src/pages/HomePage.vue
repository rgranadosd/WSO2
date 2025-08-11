<!--
  Copyright (c) 2021, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.

  WSO2 Inc. licenses this file to you under the Apache License,
  Version 2.0 (the "License"); you may not use this file except
  in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an
  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  KIND, either express or implied. See the License for the
  specific language governing permissions and limitations
  under the License.
-->

<template>
  <DefaultLayout 
    :is-loading="state.isLoading" 
    :has-errors="hasAuthenticationErrors"
  >
    <!-- Show error if clientID is not configured -->
    <div v-if="!authConfig?.clientID || authConfig?.clientID === 'your-client-id'" class="content">
      <h2>You need to update the Client ID to proceed.</h2>
      <p>
        Please open "src/config.json" file using an editor, and update
        the <code>clientID</code> value with the registered application's client ID.
      </p>
      <p>
        Visit repo 
        <a href="https://github.com/asgardeo/javascript/tree/main/packages/vue">
          README
        </a> for more details.
      </p>
    </div>

    <!-- Show authentication error -->
    <div v-else-if="hasAuthenticationErrors" class="content">
      <h2>Authentication Error</h2>
      <p>
        There was an error during the authentication process. This could be due to:
      </p>
      <ul>
        <li>Invalid Client ID configuration</li>
        <li>Server connectivity issues</li>
        <li>Application not registered in WSO2 Identity Server</li>
        <li>Incorrect redirect URLs</li>
        <li>SSL certificate issues</li>
      </ul>
      <p>
        <strong>Next steps:</strong>
      </p>
      <ol>
        <li>Check the browser console for detailed error information</li>
        <li>Verify that the application is registered in WSO2 Identity Server</li>
        <li>Ensure the Client ID matches the registered application</li>
        <li>Check that redirect URLs are correctly configured</li>
      </ol>
      <button class="btn primary" @click="handleLogin">
        {{ UI_TEXT.TRY_AGAIN }}
      </button>
    </div>

    <!-- Show logout error if user denied logout -->
    <LogoutRequestDenied
      v-else-if="hasLogoutFailureError"
      :error-message="USER_DENIED_LOGOUT"
      @login="handleLogin"
      @logout="handleLogout"
    />

    <!-- Main content when authenticated -->
    <div v-else-if="state.isAuthenticated" class="content">
      <AuthenticationResponse :derived-response="derivedAuthenticationState" />
      <button class="btn primary mt-4" @click="handleLogout">
        Logout
      </button>
    </div>

    <!-- Login page when not authenticated -->
    <div v-else class="content">
      <div class="home-image">
        <div class="vue-logo-container">
          <!-- Vue.js Logo SVG -->
          <svg 
            class="vue-logo" 
            viewBox="0 0 261.76 226.69" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <g transform="matrix(1.3333 0 0 -1.3333 -76.311 313.34)">
              <g transform="translate(178.06 235.01)">
                <path d="m0 0-22.669-39.264-22.669 39.264h-75.491l98.16-170.02 98.16 170.02z" fill="#41b883"/>
              </g>
              <g transform="translate(178.06 235.01)">
                <path d="m0 0-22.669-39.264-22.669 39.264h-36.227l58.896-102.01 58.896 102.01z" fill="#34495e"/>
              </g>
            </g>
          </svg>
          <h2 class="vue-title">Vue.js Authentication Demo</h2>
        </div>
      </div>
      <h4 class="spa-app-description">
        Sample demo to showcase authentication for a Single Page Application
        via the OpenID Connect Authorization Code flow,
        which is integrated using the&nbsp;
        <a href="https://github.com/asgardeo/javascript/tree/main/packages/vue" target="_blank" rel="noreferrer noopener">
          Asgardeo Vue SDK
        </a>&nbsp;with&nbsp;
        <a href="https://vuejs.org/" target="_blank" rel="noreferrer noopener">
          Vue.js 3.5.18
        </a>.
      </h4>
      <button class="btn primary" @click="handleLogin">
        Login
      </button>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import AuthenticationResponse from '@/components/AuthenticationResponse.vue';
import LogoutRequestDenied from '@/components/LogoutRequestDenied.vue';
import { USER_DENIED_LOGOUT, AUTH_ERROR_MESSAGES, UI_TEXT } from '@/constants/errors';
import authConfig from '../config';
// Removed image import to avoid loading issues

const route = useRoute();
const { 
  state, 
  derivedAuthenticationState, 
  signIn, 
  signOut,
  loadUserData,
  initializeAuth
} = useAuth();

const hasAuthenticationErrors = ref<boolean>(false);
const hasLogoutFailureError = ref<boolean>(false);
const loadingTimeout = ref<NodeJS.Timeout | null>(null);

// Check URL parameters for logout errors
const checkUrlParams = () => {
  const stateParam = route.query.state;
  const errorDescParam = route.query.error_description;
  
  if (stateParam && errorDescParam) {
    if (errorDescParam === "End User denied the logout request") {
      hasLogoutFailureError.value = true;
    }
  }
};

const handleLogin = async () => {
  console.log('=== LOGIN BUTTON CLICKED ===');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Auth config:', JSON.stringify(authConfig, null, 2));
  console.log('Current authentication state:', state.isAuthenticated);
  console.log('Current URL:', window.location.href);
  
  hasLogoutFailureError.value = false;
  hasAuthenticationErrors.value = false;
  
  try {
    console.log('Step 1: Testing server connectivity...');
    const response = await fetch('https://localhost:9443', {
      method: 'GET',
      mode: 'no-cors'
    });
    console.log('Step 1: Server connectivity test completed');
    console.log('Response status:', response.status);
    console.log('Response type:', response.type);
    
    console.log('Step 2: Testing SDK initialization...');
    console.log('SDK version:', '@asgardeo/auth-spa@3.3.0');
    console.log('SignIn function type:', typeof signIn);
    
    console.log('Step 3: Starting sign in process...');
    console.log('About to call signIn()...');
    await signIn();
    console.log('Step 3: Sign in completed successfully');
    
    console.log('Step 4: Checking authentication state...');
    console.log('Is authenticated after sign in:', state.isAuthenticated);
    console.log('Current URL after sign in:', window.location.href);
    
  } catch (error) {
    console.error('=== LOGIN ERROR IN HOMEPAGE ===');
    console.error('Error type:', typeof error);
    console.error('Error constructor:', error.constructor.name);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    console.error('Full error object:', error);
    console.error('Error keys:', Object.keys(error));
    
    hasAuthenticationErrors.value = true;
    alert(`${AUTH_ERROR_MESSAGES.LOGIN_FAILED}: ${error.message || AUTH_ERROR_MESSAGES.UNKNOWN_ERROR}`);
  }
};

const handleLogout = async () => {
  try {
    await signOut();
  } catch (error) {
    console.error('Logout error:', error);
  }
};

// Watch for authentication state changes and load user data
watch(() => state.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    hasAuthenticationErrors.value = false;
    await loadUserData();
  }
});

// Initialize component
onMounted(async () => {
  checkUrlParams();
  await initializeAuth();
  
  // Set a timeout to prevent infinite loading
  loadingTimeout.value = setTimeout(() => {
    if (state.isLoading) {
      console.warn('Loading timeout reached, forcing state update');
      // Force state update if stuck in loading
    }
  }, 10000); // 10 seconds timeout
});
</script>
