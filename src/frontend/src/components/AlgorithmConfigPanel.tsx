import { useState, useEffect } from "react";
import type { AlgorithmItem, AlgorithmParamSpec } from "../services/api";
import type { PipelineStep } from "../App";

type AlgorithmConfigPanelProps = {
  isCustomMode: boolean;
  algorithms: AlgorithmItem[];
  customSteps: PipelineStep[];
  onAddStep: (algorithmId: string, params: Record<string, unknown>) => void;
  onRemoveStep: (stepId: string) => void;
  onUpdateStepParam: (stepId: string, paramName: string, value: unknown) => void;
  onMoveStep: (stepId: string, direction: "up" | "down") => void;
};

function ParamInput({
  spec,
  value,
  onChange,
}: {
  spec: AlgorithmParamSpec;
  value: unknown;
  onChange: (value: unknown) => void;
}) {
  if (spec.type === "float" || spec.type === "int") {
    return (
      <input
        type="number"
        value={typeof value === "number" ? value : ""}
        min={spec.min}
        max={spec.max}
        step={spec.type === "int" ? 1 : 0.1}
        onChange={(e) =>
          onChange(
            spec.type === "int"
              ? parseInt(e.target.value, 10)
              : parseFloat(e.target.value)
          )
        }
        className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
      />
    );
  }

  if (spec.type === "list[int,int]") {
    const listValue = Array.isArray(value) ? value : [0, 0];
    return (
      <div className="mt-1 grid grid-cols-2 gap-2">
        <input
          type="number"
          value={listValue[0] ?? ""}
          onChange={(e) =>
            onChange([parseInt(e.target.value, 10), listValue[1] ?? 0])
          }
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
        />
        <input
          type="number"
          value={listValue[1] ?? ""}
          onChange={(e) =>
            onChange([listValue[0] ?? 0, parseInt(e.target.value, 10)])
          }
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
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
          onChange(
            e.target.value
              .split(",")
              .map((item) => parseFloat(item.trim()))
              .filter((item) => !Number.isNaN(item))
          )
        }
        className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
        placeholder="e.g. 15, 80, 250"
      />
    );
  }

  return (
    <input
      type="text"
      value={value === null || value === undefined ? "" : String(value)}
      onChange={(e) => onChange(e.target.value)}
      className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
    />
  );
}

function defaultParamsFor(algo: AlgorithmItem): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  Object.entries(algo.params).forEach(([k, spec]) => {
    out[k] = spec.default;
  });
  return out;
}

export default function AlgorithmConfigPanel({
  isCustomMode,
  algorithms,
  customSteps,
  onAddStep,
  onRemoveStep,
  onUpdateStepParam,
  onMoveStep,
}: AlgorithmConfigPanelProps) {
  const [pendingAlgorithmId, setPendingAlgorithmId] = useState<string>("");
  const [pendingParams, setPendingParams] = useState<Record<string, unknown>>({});
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null);

  // Set initial pending algorithm once the list arrives
  useEffect(() => {
    if (algorithms.length > 0 && !pendingAlgorithmId) {
      const first = algorithms[0];
      setPendingAlgorithmId(first.id);
      setPendingParams(defaultParamsFor(first));
    }
  }, [algorithms, pendingAlgorithmId]);

  const handlePendingAlgorithmChange = (algorithmId: string) => {
    const algo = algorithms.find((a) => a.id === algorithmId);
    if (!algo) return;
    setPendingAlgorithmId(algorithmId);
    setPendingParams(defaultParamsFor(algo));
  };

  const handleAddStep = () => {
    if (!pendingAlgorithmId) return;
    onAddStep(pendingAlgorithmId, { ...pendingParams });
  };

  const toggleExpand = (stepId: string) => {
    setExpandedStepId((prev) => (prev === stepId ? null : stepId));
  };

  const pendingAlgo = algorithms.find((a) => a.id === pendingAlgorithmId);

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 shadow-lg shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-cyan-300">Pipeline Builder</h2>
        <p className="mt-1 text-sm text-slate-400">
          Compose a custom multi-step enhancement pipeline.
        </p>
      </div>

      {!isCustomMode ? (
        <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
          Switch to{" "}
          <span className="text-slate-200">Custom Algorithm</span> mode to
          build a pipeline.
        </div>
      ) : (
        <>
          {/* ── Step list ── */}
          <div className="mb-4 space-y-2">
            {customSteps.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/50 p-6 text-center text-sm text-slate-500">
                No steps yet — add steps below to build your pipeline.
              </div>
            ) : (
              customSteps.map((step, index) => {
                const algo = algorithms.find((a) => a.id === step.algorithmId);
                const isExpanded = expandedStepId === step.stepId;

                return (
                  <div
                    key={step.stepId}
                    className="overflow-hidden rounded-xl border border-slate-700/60 bg-slate-950/70"
                  >
                    {/* Header row */}
                    <div className="flex items-center gap-3 px-4 py-3">
                      {/* Step number */}
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-cyan-500/20 text-xs font-bold text-cyan-300">
                        {index + 1}
                      </span>

                      {/* Algorithm name */}
                      <span className="flex-1 truncate text-sm font-medium text-slate-200">
                        {step.algorithmId}
                      </span>

                      {/* Controls */}
                      <div className="flex shrink-0 items-center gap-1">
                        <button
                          onClick={() => onMoveStep(step.stepId, "up")}
                          disabled={index === 0}
                          title="Move up"
                          className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-800 hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-25"
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => onMoveStep(step.stepId, "down")}
                          disabled={index === customSteps.length - 1}
                          title="Move down"
                          className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-800 hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-25"
                        >
                          ↓
                        </button>
                        <button
                          onClick={() => toggleExpand(step.stepId)}
                          className={`rounded-lg px-2 py-1 text-xs font-medium transition ${
                            isExpanded
                              ? "bg-cyan-500/20 text-cyan-300"
                              : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                          }`}
                        >
                          {isExpanded ? "Done" : "Edit"}
                        </button>
                        <button
                          onClick={() => {
                            onRemoveStep(step.stepId);
                            if (expandedStepId === step.stepId) setExpandedStepId(null);
                          }}
                          title="Remove step"
                          className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-500 transition hover:bg-red-500/20 hover:text-red-400"
                        >
                          ×
                        </button>
                      </div>
                    </div>

                    {/* Expanded param editor */}
                    {isExpanded && algo && (
                      <div className="border-t border-slate-700/60 px-4 py-4">
                        <div className="space-y-3">
                          {Object.entries(algo.params).map(([paramName, spec]) => (
                            <div key={paramName}>
                              <label className="block text-xs font-medium text-slate-400">
                                {paramName}
                                {spec.min !== undefined && spec.max !== undefined && (
                                  <span className="ml-2 text-slate-600">
                                    [{spec.min} – {spec.max}]
                                  </span>
                                )}
                              </label>
                              <ParamInput
                                spec={spec}
                                value={step.params[paramName]}
                                onChange={(value) =>
                                  onUpdateStepParam(step.stepId, paramName, value)
                                }
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* ── Add a step ── */}
          <div className="rounded-xl border border-slate-700/40 bg-slate-950/50 p-4">
            <p className="mb-3 text-sm font-semibold text-slate-300">Add a step</p>

            <div className="space-y-3">
              {/* Algorithm selector */}
              <div>
                <label className="block text-xs font-medium text-slate-400">
                  Algorithm
                </label>
                <select
                  value={pendingAlgorithmId}
                  onChange={(e) => handlePendingAlgorithmChange(e.target.value)}
                  disabled={algorithms.length === 0}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400 disabled:opacity-50"
                >
                  {algorithms.length === 0 && (
                    <option value="">Loading…</option>
                  )}
                  {algorithms.map((algo) => (
                    <option key={algo.id} value={algo.id}>
                      {algo.id}
                    </option>
                  ))}
                </select>
                {pendingAlgo?.description && (
                  <p className="mt-1 text-xs text-slate-500">
                    {pendingAlgo.description}
                  </p>
                )}
              </div>

              {/* Params for the pending step */}
              {pendingAlgo && Object.entries(pendingAlgo.params).length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-slate-400">Parameters</p>
                  {Object.entries(pendingAlgo.params).map(([paramName, spec]) => (
                    <div key={paramName}>
                      <label className="block text-xs text-slate-500">
                        {paramName}
                        {spec.min !== undefined && spec.max !== undefined && (
                          <span className="ml-2 text-slate-600">
                            [{spec.min} – {spec.max}]
                          </span>
                        )}
                      </label>
                      <ParamInput
                        spec={spec}
                        value={pendingParams[paramName]}
                        onChange={(value) =>
                          setPendingParams((prev) => ({ ...prev, [paramName]: value }))
                        }
                      />
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={handleAddStep}
                disabled={!pendingAlgorithmId}
                className="w-full rounded-xl border border-cyan-700/50 bg-cyan-500/10 py-2 text-sm font-medium text-cyan-300 transition hover:bg-cyan-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                + Add Step
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
