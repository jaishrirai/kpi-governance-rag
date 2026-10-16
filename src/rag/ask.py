"""
Command line for the pipeline. Run from the repo root:
  $env:PYTHONPATH = "src"
  python -m rag.ask "How many days do we use to count an Active Customer?"

Prints the answer, citations, whether citation validation passed, and tokens and latency.
Exit code: 0 = valid, 1 = error (details printed), 2 = answer returned but validation failed.
The answer is shown as the model gave it, even when validation fails. Every call is logged to
results/traces.jsonl.
"""
import argparse
import sys

from rag import generate, pipeline


def main(argv=None, retrieve_fn=None, generate_fn=generate.generate, trace_path=pipeline.TRACES):
    parser = argparse.ArgumentParser(prog="python -m rag.ask", description="Ask the KPI governance assistant.")
    parser.add_argument("question", nargs="+", help="the question, quoted")
    args = parser.parse_args(argv)
    question = " ".join(args.question)

    retrieve_fn = retrieve_fn or pipeline.make_retriever()
    out = pipeline.ask(question, retrieve_fn, generate_fn=generate_fn, trace_path=trace_path)

    print("Retrieved:", out.chunk_ids)
    if out.error:
        print(f"\nERROR: {out.error}", file=sys.stderr)
        print(f"(logged to {trace_path})")
        return 1
    print(f"\nrefused:   {out.refused}")
    print(f"answer:    {out.answer}")
    print(f"citations: {out.citations}")
    if out.valid:
        print("validation: OK")
    else:
        print("validation: FAILED")
        for problem in out.problems:
            print(f"  - {problem}")
    g = out.generation
    print(f"model={g.model} prompt={g.prompt_version} in={g.input_tokens} out={g.output_tokens} "
          f"thinking={g.thinking_tokens} retrieval={out.retrieval_ms:.0f} ms generation={g.latency_ms:.0f} ms")
    print(f"(logged to {trace_path})")
    return 0 if out.valid else 2


if __name__ == "__main__":
    sys.exit(main())
