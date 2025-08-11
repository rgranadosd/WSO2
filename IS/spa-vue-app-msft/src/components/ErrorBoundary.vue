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
  <div v-if="error" class="content">
    <h6 class="error-page_h6">Authentication Error</h6>
    <p class="error-page_p">
      {{ error.message || 'An error occurred during authentication. Please try again.' }}
    </p>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
interface ErrorBoundaryProps {
  error?: any;
}

defineProps<ErrorBoundaryProps>();
</script>
