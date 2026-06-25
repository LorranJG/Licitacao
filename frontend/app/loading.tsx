export default function Loading() {
  return (
    <main className="container-page py-16" aria-busy="true">
      <div className="h-12 w-72 animate-pulse rounded-xl bg-slate-200" />
      <div className="mt-10 h-32 animate-pulse rounded-2xl bg-white" />
      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="h-80 animate-pulse rounded-2xl border border-slate-200 bg-white"
          />
        ))}
      </div>
    </main>
  );
}

