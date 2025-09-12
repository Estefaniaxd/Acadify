export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-700 to-indigo-900 px-4">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-md p-8 space-y-6">
        {/* Encabezado */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-indigo-900">Bienvenido de nuevo</h1>
          <p className="text-gray-600 mt-2">Inicia sesión en <span className="text-green-500 font-semibold">Acadify</span> 🎓</p>
        </div>

        {/* Formulario */}
        <form className="space-y-5">
          {/* Correo */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Correo electrónico</label>
            <input
              type="email"
              placeholder="tucorreo@email.com"
              className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-300 focus:outline-none"
            />
          </div>

          {/* Contraseña */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-300 focus:outline-none"
            />
          </div>

          {/* Enlace para recuperar contraseña */}
          <div className="text-right text-sm">
            <a href="/forgot-password">
              <span className="text-indigo-900 font-medium hover:underline">
                ¿Olvidaste tu contraseña?
              </span>
            </a>
          </div>

          {/* Botón */}
          <button
            type="submit"
            className="w-full py-3 bg-indigo-900 text-white font-semibold rounded-xl hover:bg-green-400 transition"
          >
            Iniciar sesión
          </button>
        </form>

        {/* Enlace para registrarse */}
        <p className="text-center text-sm text-gray-600">
          ¿No tienes una cuenta?{" "}
          <a href="/register">
            <span className="text-indigo-900 font-semibold hover:underline">
              Regístrate aquí
            </span>
          </a>
        </p>
      </div>
    </div>
  );
}
