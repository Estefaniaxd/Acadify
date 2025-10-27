
import React from 'react';

export default function TratamientoDatos() {
  return (
    <section className="relative min-h-screen flex items-center justify-center py-16 px-4 bg-gradient-to-br from-violet-50 via-white to-purple-100 dark:from-gray-900 dark:via-purple-900/30 dark:to-indigo-900/30 overflow-hidden">
      {/* Fondo decorativo animado */}
      <div className="absolute inset-0 pointer-events-none select-none">
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-gradient-to-br from-primary/20 to-purple-400/10 blur-3xl" />
        <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-gradient-to-br from-pink-400/10 to-rose-500/10 blur-3xl" />
      </div>
      <div className="relative z-10 w-full max-w-3xl mx-auto rounded-3xl shadow-xl bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl border border-white/50 dark:border-gray-700/50 p-8 md:p-12">
        <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-500 to-pink-400 dark:from-yellow-300 dark:via-purple-400 dark:to-pink-400 mb-8 text-center">Política de Tratamiento de Datos</h1>
        <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-200">
          <p>
            En <span className="font-bold text-primary dark:text-yellow-300">Acadify</span>, nos comprometemos a proteger la privacidad y los datos personales de nuestros usuarios. Esta política describe cómo recopilamos, usamos, almacenamos y protegemos tu información.
          </p>
          <h2>1. Finalidad del tratamiento</h2>
          <p>
            Los datos personales se utilizan exclusivamente para la gestión de la plataforma, la personalización de la experiencia educativa, el envío de notificaciones relevantes y el cumplimiento de obligaciones legales.
          </p>
          <h2>2. Datos recolectados</h2>
          <ul>
            <li>Nombre, apellidos y datos de contacto</li>
            <li>Información académica y de uso</li>
            <li>Dirección IP y datos técnicos de acceso</li>
          </ul>
          <h2>3. Derechos del usuario</h2>
          <p>
            Puedes acceder, actualizar, rectificar o eliminar tus datos en cualquier momento. Para ejercer estos derechos, contáctanos en <a href="mailto:contacto@acadify.org" className="text-primary underline">contacto@acadify.org</a>.
          </p>
          <h2>4. Seguridad</h2>
          <p>
            Implementamos medidas técnicas y organizativas para proteger tus datos contra accesos no autorizados, pérdida o alteración.
          </p>
          <h2>5. Consentimiento</h2>
          <p>
            Al registrarte y usar Acadify, aceptas esta política de tratamiento de datos. Puedes revocar tu consentimiento en cualquier momento.
          </p>
          <h2>6. Cambios en la política</h2>
          <p>
            Acadify puede actualizar esta política. Notificaremos los cambios relevantes a través de la plataforma.
          </p>
        </div>
      </div>
    </section>
  );
}
