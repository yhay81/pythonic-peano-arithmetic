import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.mjs";

let pyodide;
let stdout = [];
let stderr = [];
let wheelSha256;

const ready = initialize();

async function resolveWheel() {
  const manifestUrl = new URL(
    "../assets/wheels/manifest.json",
    self.location.href,
  );
  const response = await fetch(manifestUrl, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Could not fetch the course wheel manifest (${response.status})`);
  }

  const manifest = await response.json();
  const wheel = manifest?.wheel;
  const sha256 = manifest?.sha256;
  if (typeof wheel !== "string" || !/^[A-Za-z0-9_.-]+\.whl$/.test(wheel)) {
    throw new Error("The course wheel manifest is invalid");
  }
  if (typeof sha256 !== "string" || !/^[0-9a-f]{64}$/.test(sha256)) {
    throw new Error("The course wheel hash is invalid");
  }
  const url = new URL(`../assets/wheels/${wheel}`, self.location.href);
  url.searchParams.set("sha256", sha256);
  return { sha256, url: url.href };
}

async function initialize() {
  self.postMessage({ type: "status", message: "Loading Python" });
  pyodide = await loadPyodide();

  pyodide.setStdout({
    batched(message) {
      stdout.push(message);
    },
  });
  pyodide.setStderr({
    batched(message) {
      stderr.push(message);
    },
  });

  self.postMessage({ type: "status", message: "Preparing the course library" });
  const wheel = await resolveWheel();
  wheelSha256 = wheel.sha256;
  await pyodide.loadPackage("micropip");
  pyodide.globals.set("_peano_wheel_url", wheel.url);
  await pyodide.runPythonAsync(`
import micropip
await micropip.install(_peano_wheel_url)
`);

  await pyodide.runPythonAsync(`
import ast

_peano_namespace = {"__name__": "__main__"}

def _peano_execute(source):
    """Execute a cell and display its final expression, like a notebook."""
    tree = ast.parse(source, filename="<course cell>", mode="exec")
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        final_expression = tree.body.pop()
        if tree.body:
            ast.fix_missing_locations(tree)
            exec(compile(tree, "<course cell>", "exec"), _peano_namespace)
        expression = ast.Expression(final_expression.value)
        ast.fix_missing_locations(expression)
        value = eval(compile(expression, "<course cell>", "eval"), _peano_namespace)
        if value is not None:
            print(repr(value))
    else:
        exec(compile(tree, "<course cell>", "exec"), _peano_namespace)
`);

  self.postMessage({ type: "ready" });
}

self.onmessage = async (event) => {
  const { type, id, code } = event.data;
  if (type !== "run") {
    return;
  }

  try {
    await ready;
    const latestWheel = await resolveWheel();
    if (latestWheel.sha256 !== wheelSha256) {
      self.postMessage({ type: "stale", id });
      return;
    }
    stdout = [];
    stderr = [];
    pyodide.globals.set("_peano_source", code);
    await pyodide.runPythonAsync("_peano_execute(_peano_source)");
    self.postMessage({
      type: "result",
      id,
      stdout: stdout.join("\n"),
      stderr: stderr.join("\n"),
    });
  } catch (error) {
    self.postMessage({
      type: "result",
      id,
      stdout: stdout.join("\n"),
      stderr: stderr.join("\n"),
      error: error instanceof Error ? error.message : String(error),
    });
  }
};

ready.catch((error) => {
  self.postMessage({
    type: "fatal",
    error: error instanceof Error ? error.message : String(error),
  });
});
