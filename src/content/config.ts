import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    updatedDate: z.date().optional(),
    category: z.string(),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
    // Schema.org 增强字段
    schemaType: z.enum(['Article', 'HowTo', 'FAQ']).optional().default('Article'),
    howToSteps: z.array(z.object({
      name: z.string(),
      text: z.string(),
    })).optional(),
    faqItems: z.array(z.object({
      question: z.string(),
      answer: z.string(),
    })).optional(),
  }),
});

export const collections = { blog };
