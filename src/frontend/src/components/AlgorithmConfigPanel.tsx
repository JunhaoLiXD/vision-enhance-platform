import type { AlgorithmItem } from "../services/api";

type AlgorithmConfigPanelProps = {
  isCustomMode: boolean;
  algorithms: AlgorithmItem[];
  selectedAlgorithmId: string;
  algorithmParams: Record<string, unknown>;
  onAlgorithmChange: (algorithmId: string) => void;
  onParamChange: (paramName: string, value: unknown) => void;
};

export default function AlgorithmConfigPanel({
  isCustomMode,
  algorithms,
  selectedAlgorithmId,
  algorithmParams,
  onAlgorithmChange,
  onParamChange,
}: AlgorithmConfigPanelProps) {
  const selectedAlgorithm = algorithms.find(
    (algorithm) => algorithm.id === selectedAlgorithmId
  );

  const renderParamInput = (paramName: string, spec: AlgorithmItem["params"][string]) => {
    const value = algorithmParams[paramName];

    if (spec.type === "float" || spec.type === "int") {
      return (
        <input
          type="number"
          value={typeof value === "number" ? value : ""}
          min={spec.min}
          max={spec.max}
          step={spec.type === "int" ? 1 : 0.1}
          onChange={(e) =>
            onParamChange(
              paramName,
              spec.type === "int" ? parseInt(e.target.value, 10) : parseFloat(e.target.value)
            )
          }
          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
        />
      );
    }

    if (spec.type === "list[int,int]") {
      const listValue = Array.isArray(value) ? value : [0, 0];

      return (
        <div className="mt-2 grid grid-cols-2 gap-3">
          <input
            type="number"
            value={listValue[0] ?? ""}
            onChange={(e) =>
              onParamChange(paramName, [parseInt(e.target.value, 10), listValue[1] ?? 0])
            }
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
          />
          <input
            type="number"
            value={listValue[1] ?? ""}
            onChange={(e) =>
              onParamChange(paramName, [listValue[0] ?? 0, parseInt(e.target.value, 10)])
            }
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
          />
        </div>
      );
    }

    if (spec.type === "list[float]") {
      return (
        <input
          type="text"
          value={Array.isArray(value) ? value.join(", ") : ""}
          onChange={(e) =>
            onParamChange(
              paramName,
              e.target.value
                .split(",")
                .map((item) => parseFloat(item.trim()))
                .filter((item) => !Number.isNaN(item))
            )
          }
          className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
          placeholder="e.g. 15, 80, 250"
        />
      );
    }

    return (
      <input
        type="text"
        value={value === null || value === undefined ? "" : String(value)}
        onChange={(e) => onParamChange(paramName, e.target.value)}
        className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
      />
    );
  };

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-cyan-300">Algorithm Configuration</h2>
        <p className="mt-1 text-sm text-slate-400">
          Choose a custom algorithm and adjust its parameters.
        </p>
      </div>

      {!isCustomMode ? (
        <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
          Switch to <span className="text-slate-200">Custom Algorithm</span> mode to configure
          a single algorithm manually.
        </div>
      ) : (
        <>
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
            <label className="block text-sm font-medium text-slate-200">
              Algorithm
            </label>

            <select
              value={selectedAlgorithmId}
              onChange={(e) => onAlgorithmChange(e.target.value)}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
            >
              {algorithms.map((algorithm) => (
                <option key={algorithm.id} value={algorithm.id}>
                  {algorithm.name}
                </option>
              ))}
            </select>

            {selectedAlgorithm?.description && (
              <p className="mt-3 text-sm text-slate-400">
                {selectedAlgorithm.description}
              </p>
            )}
          </div>

          {selectedAlgorithm && (
            <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
              <h3 className="text-sm font-medium text-slate-200">Parameters</h3>

              <div className="mt-4 space-y-4">
                {Object.entries(selectedAlgorithm.params).map(([paramName, spec]) => (
                  <div key={paramName}>
                    <label className="block text-sm text-slate-300">
                      {paramName}
                    </label>
                    {renderParamInput(paramName, spec)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}