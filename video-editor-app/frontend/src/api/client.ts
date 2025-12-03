const baseUrl = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export async function uploadEdit(videoUri: string, metadata: any, apiKey?: string) {
  const form = new FormData()
  const filename = videoUri.split('/').pop() || 'input.mp4'
  form.append('file', {
    // @ts-ignore
    uri: videoUri,
    name: filename,
    type: 'video/mp4',
  })
  form.append('metadata', JSON.stringify(metadata))
  const res = await fetch(`${baseUrl}/upload`, {
    method: 'POST',
    headers: apiKey ? { 'x-api-key': apiKey } : undefined,
    body: form,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getStatus(jobId: string) {
  const res = await fetch(`${baseUrl}/status/${jobId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export function resultUrl(jobId: string) {
  return `${baseUrl}/result/${jobId}`
}
