import { getRssString } from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET() {
  const posts = await getCollection('blog');
  const rssString = await getRssString({
    title: '异宠指南',
    description: '中国第一个异宠新手系统化饲养指南——守宫、玉米蛇、鬃狮蜥、角蛙全面饲养知识',
    site: 'https://yichongzhinan.com',
    items: posts.map(post => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}`,
    })),
  });
  return new Response(rssString, {
    headers: { 'Content-Type': 'application/xml' },
  });
}
