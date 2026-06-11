import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: process.env.PUBLIC_SITE_URL || 'https://yi-chong-guide.pages.dev',
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
