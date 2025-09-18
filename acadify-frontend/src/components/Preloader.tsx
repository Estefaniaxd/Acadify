import { useEffect } from "react";
import loaderVideo from "./images/icons/loader.mp4"; // asegúrate de que el path es correcto

export default function Preloader({ onFinish }: { onFinish: () => void }) {
  useEffect(() => {
    const id = setTimeout(() => onFinish(), 1500); // Ajusta el tiempo si quieres
    return () => clearTimeout(id);
  }, [onFinish]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-4 animate-fade-in">
        {/* Video loader */}
        <video
          src={loaderVideo}
          autoPlay
          loop
          muted
          playsInline
          className="w-28 h-28 rounded-full"
        />

        {/* Texto de carga */}
        <div className="text-sm text-gray-600">
          .·:*¨¨*Cargando Acadify*¨¨*:·.
        </div>
      </div>
    </div>
  );
}
