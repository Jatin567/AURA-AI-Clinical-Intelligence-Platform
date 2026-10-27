import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  // Dashboard exports at the project root are archived reference material, not
  // application source.  Restrict linting to the runnable client instead.
  globalIgnores(['dist', 'Dashboard_*.jsx']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', {
        varsIgnorePattern: '^[A-Z_]|motion',
        argsIgnorePattern: '^[A-Z_]|motion',
      }],
    },
  },
  {
    files: ['src/engine/CardRegistry.jsx'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
])
