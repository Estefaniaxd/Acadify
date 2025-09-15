import RutilioImg from "./images/rutiliolike.png";

export default function MascotCard({ imgSrc }: { imgSrc?: string }) {
  return (
    <div className="w-72 p-4 rounded-xl bg-white shadow flex flex-col items-center gap-3">
      <div className="w-36 h-36 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
        <img
          src={imgSrc || RutilioImg}
          alt="Rutilio"
          className="object-cover w-full h-full"
        />
      </div>
      <h4 className="font-semibold text-purple-500">Rutilio</h4>
      <p className="text-sm text-center text-gray-600">
        Nuestra compañía virtual y amigable que acompaña a estudiantes durante
        su camino de aprendizaje.
      </p>
    </div>
  );
}

