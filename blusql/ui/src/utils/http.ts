import { type Http, http } from '@aleph-alpha/lib-http'
import type { CustomRagResponse, CustomRagRequest } from '@/@core/models/api/customRag.ts'

export const HTTP_CLIENT = http({ timeout: 60_000 })

export class CustomRagService {
  constructor(readonly httpClient: Http) {}

  async customQa(body: CustomRagRequest): Promise<CustomRagResponse> {
    return (
      await this.httpClient.post<CustomRagResponse>(
        'v1/skills/customer-playground/generate-bluesql/run',
        { body },
      )
    ).data
  }
}

export const CUSTOM_RAG_SERVICE = new CustomRagService(HTTP_CLIENT)

// import type { CustomRagResponse, CustomRagRequest } from '@/@core/models/api/customRag.ts'

// Sleep function
// function sleep(ms: number) {
//   return new Promise((resolve) => setTimeout(resolve, ms))
// }

// export class MockCustomRagService {
//   async customQa(body: CustomRagRequest): Promise<CustomRagResponse> {
//     await sleep(2000)
//     return {
//       query: body.question,
//       markdown: `**Mocked answer for:** ${body.question}`,
//       explanation: 'This is a mock response for testing purposes.',
//     }
//   }
// }

// export const CUSTOM_RAG_SERVICE = new MockCustomRagService()
