import { useState } from "react";
import ConfigTable from "./components/ConfigTable";
import AgentChat from "./components/AgentChat";

export default function App() {
  const [activeTab, setActiveTab] = useState<"table" | "chat">("table");

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-6 py-3">
        <h1 className="text-xl font-bold text-gray-800">Config Agent</h1>
        <p className="text-xs text-gray-500">
          Microservices configuration management
        </p>
      </header>

      {/* Mobile tab toggle */}
      <div className="flex border-b border-gray-200 bg-white md:hidden">
        <button
          onClick={() => setActiveTab("table")}
          className={`flex-1 py-2 text-sm font-medium ${
            activeTab === "table"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-500"
          }`}
        >
          Configs
        </button>
        <button
          onClick={() => setActiveTab("chat")}
          className={`flex-1 py-2 text-sm font-medium ${
            activeTab === "chat"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-500"
          }`}
        >
          Agent Chat
        </button>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Config table — left panel */}
        <div
          className={`flex-[7] overflow-hidden ${
            activeTab !== "table" ? "hidden md:block" : ""
          }`}
        >
          <ConfigTable />
        </div>

        {/* Agent chat — right panel */}
        <div
          className={`flex-[3] overflow-hidden ${
            activeTab !== "chat" ? "hidden md:block" : ""
          }`}
        >
          <AgentChat />
        </div>
      </div>
    </div>
  );
}
