export default function formatApiError(data: any): string {
  if (!data) return 'Error del servidor. Intenta de nuevo.'

  // FastAPI/Pydantic often returns { detail: [...] }
  if (data.detail) {
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: any) => {
        if (!d) return ''
        if (typeof d === 'string') return d
        // d can be { loc, msg, type }
        if (d.msg) {
          try {
            const loc = Array.isArray(d.loc) ? d.loc.join('.') : String(d.loc)
            return `${loc ? loc + ': ' : ''}${d.msg}`
          } catch {
            return d.msg
          }
        }
        if (d.message) return String(d.message)
        return JSON.stringify(d)
      }).filter(Boolean).join(' | ')
    }
    return String(data.detail)
  }

  if (data.message) return String(data.message)
  if (typeof data === 'string') return data
  try {
    return JSON.stringify(data)
  } catch {
    return 'Error desconocido del servidor.'
  }
}
