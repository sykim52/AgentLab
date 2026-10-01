export function BenchmarksPage() {
  return (
    <section>
      <h1>Benchmarks</h1>
      <p className="muted">
        Measured results only — no placeholder numbers. Fill after Llama / Mistral / Qwen
        inference runs and Python vs C++ parser benches.
      </p>
      <h2>Model Benchmark</h2>
      <p>See <code>docs/benchmarks/models/</code> (Planned).</p>
      <h2>Runtime Benchmark</h2>
      <ul>
        <li>Python parser vs C++ LogParser</li>
        <li>Transformers vs vLLM vs OpenAI-compatible GPU serving (when hardware evidence exists)</li>
      </ul>
    </section>
  );
}
