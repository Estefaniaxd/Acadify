import { useState } from "react";
import ojoAbierto from "../images/icons/ojo-abierto.png"
import ojoCerrado from "../images/icons/ojo-cerrado.png"

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-700 to-indigo-900 px-4">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-md p-8 space-y-6">
        {/* Encabezado */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-indigo-900">Bienvenido de nuevo</h1>
          <p className="text-gray-600 mt-2">
            Inicia sesión en <span className="text-green-500 font-semibold">Acadify</span> ☆
          </p>
        </div>

        {/* Formulario */}
        <form className="space-y-5">
          {/* Correo */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Correo electrónico
            </label>
            <input
              type="email"
              placeholder="tucorreo@email.com"
              className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-300 focus:outline-none"
            />
          </div>

          {/* Contraseña */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Contraseña
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-300 focus:outline-none pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                <img
                  src={showPassword ? ojoCerrado : ojoAbierto}
                  alt="Mostrar contraseña"
                  className="w-20 h-20"
                />
              </button>
            </div>
          </div>

          {/* Enlace para recuperar contraseña */}
          <div className="text-right text-sm">
            <a href="/forgot-password">
              <span className="text-indigo-900 font-medium hover:underline">
                ¿Olvidaste tu contraseña?
              </span>
            </a>
          </div>

          {/* Botón principal */}
          <button
            type="submit"
            className="w-full py-3 bg-indigo-900 text-white font-semibold rounded-xl hover:bg-green-400 transition"
          >
            Iniciar sesión
          </button>
        </form>

        {/* Separador */}
        <div className="flex items-center gap-2">
          <hr className="flex-grow border-gray-300" />
          <span className="text-sm text-gray-500">o continúa con</span>
          <hr className="flex-grow border-gray-300" />
        </div>

        {/* Botones sociales */}
        <div className="flex flex-col gap-3">
          <button
            type="button"
            className="flex items-center justify-center gap-3 w-full py-3 border border-gray-300 rounded-xl hover:border-indigo-900 transition"
          >
            <img
              src="src/components/images/icons/icon-gmail.png"
              alt="Google"
              className="w-10 h-10"
            />
            <span className="text-gray-700 font-medium">Iniciar con Gmail</span>
          </button>
        </div>

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
