import { type Http, http } from '@aleph-alpha/lib-http'
import type { CustomRagResponse, CustomRagRequest } from '@/@core/models/api/customRag.ts'

export const HTTP_CLIENT = http({ timeout: 60_000 })

export class CustomRagService {
  constructor(readonly httpClient: Http) {}

  async customQa(body: CustomRagRequest): Promise<CustomRagResponse> {
    return (await this.httpClient.post<CustomRagResponse>('generate-bluesql', { body })).data
    // return (
    //   await this.httpClient.post<CustomRagResponse>(
    //     'v1/skills/customer-playground/generate-bluesql/run',
    //     { body },
    //   )
    // ).data
  }
}

export const CUSTOM_RAG_SERVICE = new CustomRagService(HTTP_CLIENT)

// import type { CustomRagResponse, CustomRagRequest } from '@/@core/models/api/customRag.ts'

// function sleep(ms: number) {
//   return new Promise((resolve) => setTimeout(resolve, ms))
// }

// export class MockCustomRagService {
//   async customQa(body: CustomRagRequest): Promise<CustomRagResponse> {
//     await sleep(2000)
//     return {
//       sql_query: `SELECT p.id, p.name, SUM(o.total) AS total_sales
// FROM products p
// JOIN orders o ON o.product_id = p.id
// WHERE p.active = TRUE
// GROUP BY p.id, p.name
// HAVING SUM(o.total) > 500`,
//       markdown_result: `| Product Name | Category   | Price | In Stock |
// |--------------|------------|-------|----------|
// | Apple        | Fruit      | $1    | Yes      |
// | Carrot       | Vegetable  | $0.5  | No       |
// | Bread        | Bakery     | $2    | Yes      |
// | Milk         | Dairy      | $1.2  | Yes      |`,
//       explanation: 'This is a mock response for testing purposes.',
//     }
//   }
// }

// export const CUSTOM_RAG_SERVICE = new MockCustomRagService()
