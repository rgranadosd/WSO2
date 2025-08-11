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
  <div>
    <div class="container">
      <div class="header-title">
        <h1>Vue.js 3.5.18 SPA Authentication Sample</h1>
      </div>
      <div v-if="isLoading" class="content">
        Loading ...
      </div>
      <div v-else-if="hasErrors" class="content">
        An error occurred while authenticating ...
      </div>
      <div v-else>
        <slot />
      </div>
    </div>
    <img :src="footerLogos" class="footer-image" />
  </div>
</template>

<script setup lang="ts">
import footerLogos from '@/assets/images/footer.png';

interface DefaultLayoutProps {
  isLoading?: boolean;
  hasErrors?: boolean;
}

defineProps<DefaultLayoutProps>();
</script>
