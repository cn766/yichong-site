import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://yichongzhinan.com',
  integrations: [sitemap()],
  build: {
    format: 'file',
    inlineStylesheets: 'auto',
  },
  trailingSlash: 'never',
  compressHTML: true,
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  },
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: true,
    },
    remarkPlugins: [],
    rehypePlugins: [],
  },
  vite: {
    build: {
      cssMinify: true,
      minify: true,
    },
    css: {
      devSourcemap: true,
    },
  },
});
