import React from 'react';

export default function Consentimiento() {
  return (
    <section className="max-w-3xl mx-auto py-16 px-4">
      <h1 className="text-3xl md:text-4xl font-extrabold text-primary mb-6">Consentimiento Informado</h1>
      <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-200">
        <p>
          Al registrarte y utilizar Acadify, otorgas tu consentimiento para el tratamiento de tus datos personales conforme a la <a href="/legal/TratamientoDatos" className="text-primary underline">Política de Tratamiento de Datos</a>.
        </p>
        <h2>¿Qué implica tu consentimiento?</h2>
        <ul>
          <li>Permites que Acadify procese tus datos para fines educativos y administrativos.</li>
          <li>Autorizas el envío de notificaciones relevantes a tu correo electrónico.</li>
          <li>Reconoces tu derecho a revocar este consentimiento en cualquier momento.</li>
        </ul>
        <h2>¿Cómo puedes revocar tu consentimiento?</h2>
        <p>
          Puedes solicitar la revocatoria de tu consentimiento y la eliminación de tus datos escribiendo a <a href="mailto:contacto@acadify.org" className="text-primary underline">contacto@acadify.org</a>.
        </p>
        <h2>Más información</h2>
        <p>
          Consulta la <a href="/legal/TratamientoDatos" className="text-primary underline">Política de Tratamiento de Datos</a> para conocer todos los detalles sobre el uso y protección de tu información.
        </p>
      </div>
    </section>
  );
}
