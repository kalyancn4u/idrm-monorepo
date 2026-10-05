import { defineConfig } from '@kubb/core';
import { pluginOas } from '@kubb/plugin-oas';
import { pluginTs } from '@kubb/plugin-ts';
import { pluginClient } from '@kubb/plugin-client';

export default defineConfig({
  root: '.',
  input: { path: './shared/contracts/v1/openapi.json' },
  output: { path: './packages/api-client/src/gen' },
  plugins: [pluginOas(), pluginTs(), pluginClient()],
});
