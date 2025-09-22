

import { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import formatApiError from '../../utils/formatApiError'

export default function RecoverPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  function validate() {
    if (!email) return 'El email es obligatorio.'
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return 'Email inválido.'
    return ''
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const err = validate()
    if (err) return setError(err)
    setError('')
    setLoading(true)
    try {
      await axios.post(
        '/auth/forgot-password',
        { correo_institucional: email },
        {
          withCredentials: true,
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      setSent(true)
    } catch (err: any) {
      if (err.response && err.response.data) {
        setError(formatApiError(err.response.data))
      } else {
        setError('Error al enviar la solicitud. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-8 bg-white dark:bg-[#0b0b0b] rounded-lg shadow w-full max-w-md mx-auto">
      <h2 className="text-2xl font-semibold text-primary mb-4">Recuperar contraseña</h2>
      {sent ? (
        <div className="text-green-600 text-sm mb-4">
          Si el email existe, recibirás instrucciones para restablecer tu contraseña. Puedes seguir el enlace para ingresar el código que te enviamos o pegarlo en el formulario.
          <div className="mt-2">
            <a className="text-sm text-primary hover:underline" href={`/reset-password?correo_institucional=${encodeURIComponent(email)}`}>Ir a restablecer contraseña</a>
          </div>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <label className="block text-sm mb-1" htmlFor="email">Email</label>
            <input id="email" type="email" autoComplete="username" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={email} onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} required />
          </div>
          {error && <div className="mb-3 text-red-600 text-sm">{error}</div>}
          <button type="submit" className="w-full py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors" disabled={loading}>
            {loading ? 'Enviando...' : 'Enviar instrucciones'}
          </button>
          <div className="mt-4 text-center">
            <a href="/reset-password" className="text-sm text-primary hover:underline">¿Ya tienes el código? Restablecer contraseña</a>
          </div>
        </>
      )}
    </form>
  )
}
