import React from 'react';

export default function TratamientoDatos() {
  return (
    <section className="max-w-3xl mx-auto py-16 px-4">
      <h1 className="text-3xl md:text-4xl font-extrabold text-primary mb-6">Política de Tratamiento de Datos</h1>
      <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-200">
        <p>
          En Acadify, nos comprometemos a proteger la privacidad y los datos personales de nuestros usuarios. Esta política describe cómo recopilamos, usamos, almacenamos y protegemos tu información.
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
    </section>
  );
}
