import { z } from 'zod'

export interface CustomRagRequest {
  natural_query: string
}

export const CUSTOM_RAG_RESPONSE_SCHEMA = z.object({
  sql_query: z.string(),
  markdown_result: z.string(),
  explanation: z.string().optional(),
})

export type CustomRagResponse = z.infer<typeof CUSTOM_RAG_RESPONSE_SCHEMA>
