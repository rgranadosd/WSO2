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
  <div class="auth-response-container">
    <h2>Authentication Response</h2>
    <h4 class="sub-title">
      Derived by the&nbsp;
      <code class="inline-code-block">
        <a href="https://www.npmjs.com/package/@asgardeo/auth-spa/v/latest"
           target="_blank"
           rel="noreferrer"
        >
          @asgardeo/auth-spa
        </a>
      </code>&nbsp;SDK
    </h4>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <h3>{{ LOADING_MESSAGES.PROCESSING_AUTH }}</h3>
      <p>{{ LOADING_MESSAGES.PROCESSING_AUTH_DESCRIPTION }}</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error">
      <h3>{{ AUTH_ERROR_MESSAGES.AUTHENTICATION_ERROR }}</h3>
      <p>{{ error }}</p>
      <button @click="$router.push(URL_CONSTANTS.HOME)" class="btn primary">{{ UI_TEXT.GO_BACK_TO_HOME }}</button>
    </div>
    
    <!-- Success state -->
    <div v-else-if="derivedResponse" class="success-content">
      <!-- User Info Section -->
      <div class="section">
        <h3>{{ UI_TEXT.USER_INFORMATION }}</h3>
        <div class="json">
          <div class="asg-json-viewer">
            <pre>{{ formatJson(derivedResponse?.authenticateResponse) }}</pre>
          </div>
        </div>
      </div>

      <!-- ID Token Section -->
      <div class="section">
        <h3>{{ UI_TEXT.ID_TOKEN }}</h3>
        <div class="token-layout">
          <!-- Encoded Column -->
          <div class="token-column encoded-column">
            <h4>{{ UI_TEXT.ENCODED }}</h4>
            <div class="encoded-token">
              <div class="token-part">
                <span class="part-label">{{ UI_TEXT.HEADER }}:</span>
                <div class="token-segment header-segment">
                  {{ derivedResponse?.idToken[0] }}
                </div>
              </div>
              <div class="token-part">
                <span class="part-label">{{ UI_TEXT.PAYLOAD }}:</span>
                <div class="token-segment payload-segment">
                  {{ derivedResponse?.idToken[1] }}
                </div>
              </div>
              <div class="token-part">
                <span class="part-label">{{ UI_TEXT.SIGNATURE }}:</span>
                <div class="token-segment signature-segment">
                  {{ derivedResponse?.idToken[2] }}
                </div>
              </div>
            </div>
          </div>

          <!-- Decoded Column -->
          <div class="token-column decoded-column">
            <div class="decoded-section">
              <h4>{{ UI_TEXT.DECODED }}: {{ UI_TEXT.HEADER }}</h4>
              <div class="asg-json-viewer">
                <pre>{{ formatJson(derivedResponse?.decodedIdTokenHeader) }}</pre>
              </div>
            </div>

            <div class="decoded-section">
              <h4>{{ UI_TEXT.DECODED }}: {{ UI_TEXT.PAYLOAD }}</h4>
              <div class="asg-json-viewer">
                <pre>{{ formatJson(derivedResponse?.decodedIDTokenPayload) }}</pre>
              </div>
            </div>

            <div class="decoded-section">
              <h4>{{ UI_TEXT.SIGNATURE }}</h4>
              <div class="signature-info">
                <code>
                  HMACSHA256(<br/>
                  &nbsp;&nbsp;<span class="id-token-0">base64UrlEncode(
                                  <span class="id-token-1">header</span>)</span> + "." + <br/>
                  &nbsp;&nbsp;<span class="id-token-0">base64UrlEncode(
                                  <span class="id-token-1">payload</span>)</span>,&nbsp;
                  <span class="id-token-1">your-256-bit-secret</span> <br/>
                  );
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="logout-section">
        <button
          class="btn primary mt-4"
          @click="handleLogout"
          :disabled="isLoggingOut"
        >
          {{ isLoggingOut ? LOADING_MESSAGES.LOGGING_OUT : LOADING_MESSAGES.LOGOUT }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import type { DerivedState } from '@/composables/useAuth';
import { AUTH_ERROR_MESSAGES, URL_CONSTANTS, LOADING_MESSAGES, UI_TEXT } from '@/constants/errors';

const derivedResponse = ref<DerivedState | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const isLoggingOut = ref(false);

const { signOut } = useAuth();

const handleLogout = async () => {
  try {
    isLoggingOut.value = true;
    console.log('Starting logout process...');
    
    await signOut();
    
    // The signOut method should handle the redirect automatically
    // If we reach here, it means the redirect didn't happen
    console.log('Logout completed, redirecting to home...');
    window.location.href = URL_CONSTANTS.HOME;
    
  } catch (err) {
    console.error('Error during logout:', err);
    
    // Show user-friendly error message
    if (err.message && err.message.includes('OAuth')) {
      error.value = AUTH_ERROR_MESSAGES.OAUTH_PROCESSING_FAILED;
    } else {
      error.value = `${AUTH_ERROR_MESSAGES.LOGOUT_ERROR}: ${err instanceof Error ? err.message : String(err)}`;
    }
    
    // Reset loading state
    isLoggingOut.value = false;
  }
};

onMounted(async () => {
  // Only run in browser environment
  if (typeof window === 'undefined') {
    console.log('Skipping authentication processing - not in browser environment');
    return;
  }

  try {
    console.log('AuthenticationResponse: Processing callback...');
    console.log('Current URL:', window.location.href);
    
    // Check if we have authorization code in URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const errorParam = urlParams.get('error');
    
    console.log('Authorization code:', code);
    console.log('Error parameter:', errorParam);
    
    if (errorParam) {
      error.value = `Authentication error: ${errorParam}`;
      loading.value = false;
      return;
    }
    
    if (!code) {
      // If no authorization code, redirect to home page instead of showing error
      console.log('No authorization code found, redirecting to home page...');
      window.location.href = URL_CONSTANTS.HOME;
      return;
    }
    
    console.log('Processing authorization code...');
    
    // Use the existing composable
    const { signIn, derivedAuthenticationState } = useAuth();
    
    console.log('Calling signIn to complete authentication...');
    await signIn();
    
    console.log('Getting derived state...');
    if (derivedAuthenticationState.value) {
      derivedResponse.value = derivedAuthenticationState.value;
      console.log('Derived response set:', derivedResponse.value);
    } else {
      error.value = AUTH_ERROR_MESSAGES.FAILED_TO_LOAD_USER_DATA;
    }
    
    loading.value = false;
    
  } catch (err) {
    console.error('Error processing authentication response:', err);
    error.value = `${AUTH_ERROR_MESSAGES.AUTHENTICATION_ERROR}: ${err instanceof Error ? err.message : String(err)}`;
    loading.value = false;
  }
});

// Simple JSON display component since @textea/json-viewer might not work directly in Vue
const formatJson = (obj: any) => {
  return JSON.stringify(obj, null, 2);
};
</script>

<style scoped>
.auth-response-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  text-align: left;
}

.auth-response-container h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #2A2A2A;
}

.auth-response-container h3 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #2A2A2A;
  border-bottom: 2px solid #f47421;
  padding-bottom: 0.5rem;
}

.auth-response-container h4 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: #2A2A2A;
  font-weight: 600;
}

.sub-title {
  margin-top: 0;
  font-size: 1.3rem;
  margin-bottom: 2rem;
  color: #666;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.loading h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.loading p {
  font-size: 1.1rem;
  color: #666;
}

.error {
  text-align: center;
  padding: 2rem;
  color: #9f3a38;
  font-size: 1.2rem;
}

.error h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.error p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.success-content {
  margin-top: 2rem;
}

.section {
  margin-bottom: 3rem;
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.json {
  text-align: left;
  display: block;
  overflow: auto;
  word-break: break-all;
  margin-bottom: 1rem;
}

.asg-json-viewer {
  background-color: #272822 !important;
  padding: 25px;
  color: #f9f8f5;
  border-radius: 4px;
  font-size: 1.1rem;
  line-height: 1.6;
}

.asg-json-viewer pre {
  margin: 0;
  color: #f9f8f5;
  font-family: Monaco, Consolas, "Andale  Mono", "DejaVu Sans Mono", monospace;
  font-size: 1.1rem;
  line-height: 1.6;
}

.token-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-top: 1rem;
}

.token-column {
  display: flex;
  flex-direction: column;
}

.encoded-column {
  min-width: 0;
}

.decoded-column {
  min-width: 0;
}

.encoded-token {
  background: #272822;
  padding: 1.5rem;
  border-radius: 4px;
  font-family: Monaco, Consolas, "Andale  Mono", "DejaVu Sans Mono", monospace;
}

.token-part {
  margin-bottom: 1.5rem;
}

.token-part:last-child {
  margin-bottom: 0;
}

.part-label {
  display: block;
  color: #f9f8f5;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.token-segment {
  background: #1e1e1e;
  padding: 1rem;
  border-radius: 3px;
  font-size: 0.9rem;
  line-height: 1.4;
  word-break: break-all;
  border-left: 4px solid;
}

.header-segment {
  color: #cc6633;
  border-left-color: #cc6633;
}

.payload-segment {
  color: #f9f8f5;
  border-left-color: #f9f8f5;
}

.signature-segment {
  color: #fd971f;
  border-left-color: #fd971f;
}

.decoded-section {
  margin-bottom: 2rem;
}

.decoded-section:last-child {
  margin-bottom: 0;
}

.signature-info {
  background: #272822;
  padding: 1.5rem;
  border-radius: 4px;
  font-family: Monaco, Consolas, "Andale  Mono", "DejaVu Sans Mono", monospace;
  font-size: 1rem;
  line-height: 1.6;
}

.signature-info code {
  color: #f9f8f5;
}

.id-token-0 {
  color: #cc6633;
}

.id-token-1 {
  color: #f9f8f5;
}

.logout-section {
  text-align: center;
  margin-top: 2rem;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.btn.primary {
  background-color: #282c34;
  border-radius: 3px;
  border: none;
  color: #ffffff;
  display: inline-block;
  font-size: 1.14285714rem;
  text-align: center;
  text-decoration: none;
  width: 150px;
  cursor: pointer;
  -webkit-text-size-adjust: none;
  padding: .78571429em 1.5em .78571429em;
  margin-top: 30px;
  outline: none;
}

.btn.primary:hover:not(:disabled) {
  background-color: #1a1d23;
}

.btn.primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.inline-code-block {
  border-radius: 6px;
  -moz-border-radius: 6px;
  -webkit-border-radius: 6px;
  padding: 3px 5px;
  border: 1px solid #cdcdcd;
  background-color: white;
  font-family: Monaco, Consolas, "Andale  Mono", "DejaVu Sans Mono", monospace;
}

.inline-code-block a {
  text-decoration: none !important;
}

@media screen and (max-width: 1200px) {
  .token-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .encoded-token {
    padding: 1rem;
  }
  
  .token-segment {
    font-size: 0.8rem;
    padding: 0.8rem;
  }
}

@media screen and (max-width: 768px) {
  .auth-response-container {
    padding: 0 20px;
  }
  
  .section {
    padding: 1.5rem;
  }
  
  .auth-response-container h2 {
    font-size: 2rem;
  }
  
  .auth-response-container h3 {
    font-size: 1.5rem;
  }
  
  .auth-response-container h4 {
    font-size: 1.2rem;
  }
  
  .asg-json-viewer {
    font-size: 1rem;
    padding: 20px;
  }
  
  .asg-json-viewer pre {
    font-size: 1rem;
  }
  
  .token-segment {
    font-size: 0.75rem;
    padding: 0.6rem;
  }
}
</style>
