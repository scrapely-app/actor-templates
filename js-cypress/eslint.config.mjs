import prettier from 'eslint-config-prettier';
import pluginCypress from 'eslint-plugin-cypress/flat';

export default [{ ignores: ['**/dist'] }, pluginCypress.configs.recommended, prettier];
