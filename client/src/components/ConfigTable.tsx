import { useState, useEffect, useCallback } from "react";
import type { ConfigEntry } from "../types";
import { getConfigs, getServices, getEnvironments } from "../services/api";

export default function ConfigTable() {
  const [configs, setConfigs] = useState<ConfigEntry[]>([]);
  const [services, setServices] = useState<string[]>([]);
  const [environments, setEnvironments] = useState<string[]>([]);
  const [filterService, setFilterService] = useState("");
  const [filterEnv, setFilterEnv] = useState("");
  const [error, setError] = useState("");

  const fetchConfigs = useCallback(async () => {
    try {
      const data = await getConfigs({
        service_name: filterService || undefined,
        environment: filterEnv || undefined,
      });
      setConfigs(data);
      setError("");
    } catch {
      setError("Failed to load configs. Is the services API running?");
    }
  }, [filterService, filterEnv]);

  // Fetch filter options on mount
  useEffect(() => {
    getServices().then(setServices).catch(() => {});
    getEnvironments().then(setEnvironments).catch(() => {});
  }, []);

  // Fetch configs on mount, filter change, and every 10s
  useEffect(() => {
    fetchConfigs();
    const interval = setInterval(fetchConfigs, 10000);
    return () => clearInterval(interval);
  }, [fetchConfigs]);

  return (
    <div className="flex h-full flex-col p-4">
      {/* Header + Filters */}
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <h2 className="text-lg font-semibold text-gray-800">Configurations</h2>
        <select
          value={filterService}
          onChange={(e) => setFilterService(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        >
          <option value="">All Services</option>
          {services.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={filterEnv}
          onChange={(e) => setFilterEnv(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        >
          <option value="">All Environments</option>
          {environments.map((e) => (
            <option key={e} value={e}>
              {e}
            </option>
          ))}
        </select>
        <button
          onClick={fetchConfigs}
          className="rounded bg-gray-100 px-3 py-1 text-sm text-gray-600 hover:bg-gray-200"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto rounded border border-gray-200">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-4 py-3">Service</th>
              <th className="px-4 py-3">Environment</th>
              <th className="px-4 py-3">Key</th>
              <th className="px-4 py-3">Value</th>
              <th className="px-4 py-3">Updated At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {configs.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-medium">{c.service_name}</td>
                <td className="px-4 py-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      c.environment === "prod"
                        ? "bg-red-100 text-red-700"
                        : c.environment === "staging"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                    }`}
                  >
                    {c.environment}
                  </span>
                </td>
                <td className="px-4 py-2 font-mono text-xs">{c.config_key}</td>
                <td className="px-4 py-2 font-mono text-xs">{c.config_value}</td>
                <td className="px-4 py-2 text-xs text-gray-500">
                  {new Date(c.updated_at).toLocaleString()}
                </td>
              </tr>
            ))}
            {configs.length === 0 && !error && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                  No configurations found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
