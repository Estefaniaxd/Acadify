
const items = [
{title:'Diseño UX', desc:'Interfaz clara y accesible'},
{title:'Seguimiento', desc:'Analíticas de progreso'},
{title:'Gamificación', desc:'Motiva el aprendizaje'}
]


export default function Features(){
return (
<section className="mt-10">
<h3 className="text-2xl font-semibold text-center">Características</h3>
<div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
{items.map(it=> (
<div key={it.title} className="p-6 rounded-xl bg-white shadow-sm">
<div className="font-semibold mb-2" style={{color:'var(--purple)'}}>{it.title}</div>
<div className="text-sm text-gray-600">{it.desc}</div>
</div>
))}
</div>
</section>
)
}