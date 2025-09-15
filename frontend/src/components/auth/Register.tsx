import { useState } from "react";
import ojoAbierto from "../images/icons/ojo-abierto.png";
import ojoCerrado from "../images/icons/ojo-cerrado.png";

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-700 to-indigo-900 px-4">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-lg p-8 space-y-6">
        {/* Título */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-indigo-900">Crear cuenta</h1>
          <p className="text-gray-600 mt-2">
            Regístrate en{" "}
            <span className="text-green-500 font-semibold">Acadify</span> y
            comienza tu experiencia educativa
          </p>
        </div>

        {/* Formulario */}
        <form className="space-y-4">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Nombre</label>
            <input
              type="text"
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
            />
          </div>

          {/* Apellidos */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Apellidos</label>
            <input
              type="text"
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
            />
          </div>

          {/* Tipo documento */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Tipo de documento</label>
            <select className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-300">
              <option value="">Selecciona</option>
              <option value="CC">Cédula de ciudadanía</option>
              <option value="TI">Tarjeta de identidad</option>
              <option value="CE">Cédula de extranjería</option>
              <option value="PP">Pasaporte</option>
            </select>
          </div>

          {/* Número documento */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Número de documento</label>
            <input
              type="text"
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
            />
          </div>

          {/* Teléfono */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Teléfono</label>
            <input
              type="tel"
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
            />
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Descripción</label>
            <textarea
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
              rows={3}
            ></textarea>
          </div>

          {/* Correo */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Correo electrónico</label>
            <input
              type="email"
              className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300"
            />
          </div>

          {/* Contraseña */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Contraseña</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300 pr-10"
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

          {/* Confirmar contraseña */}
          <div>
            <label className="block text-sm font-medium text-indigo-700">Confirmar contraseña</label>
            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                className="w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-green-300 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                <img
                  src={showConfirm ? ojoCerrado : ojoAbierto}
                  alt="Mostrar confirmación"
                  className="w-20 h-20"
                />
              </button>
            </div>
          </div>

          {/* Botón */}
          <button
            type="submit"
            className="w-full py-3 bg-indigo-900 text-white font-semibold rounded-xl hover:bg-green-400 transition"
          >
            Registrarse
          </button>
        </form>

        {/* Enlace a login */}
        <p className="text-center text-sm text-gray-600">
          ¿Ya tienes cuenta?{" "}
          <a
            href="/login"
            className="text-indigo-900 font-semibold hover:underline"
          >
            Inicia sesión aquí
          </a>
        </p>
      </div>
    </div>
  );
}
