/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useState, useRef, FormEvent } from "react";
import { 
  Bot, RefreshCw, AlertTriangle, MessageSquare, Sliders, 
  Activity, Settings, Send, Users, Compass, CheckCircle, Clock 
} from "lucide-react";

export default function App() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isActionPending, setIsActionPending] = useState<boolean>(false);
  
  // Navigation
  const [activeTab, setActiveTab] = useState<"live" | "targeting">("live");

  // Targeting Form State
  const [sectorsInput, setSectorsInput] = useState("");
  const [citiesInput, setCitiesInput] = useState("");
  const [titlesInput, setTitlesInput] = useState("");
  const [intervalInput, setIntervalInput] = useState(2);
  const [limitInput, setLimitInput] = useState(15);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // AI Chat State
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{role: string; content: string}>>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const fetchDashboard = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/dashboard");
      if (!response.ok) throw new Error("Network response was not ok");
      const result = await response.json();
      
      // Load chat history only after a successful dashboard sync is confirmed
      if (error || !data) {
        fetchChatHistory();
      }

      setData(result);
      
      // Initialize targeting form once data is loaded
      if (result) {
        setSectorsInput(result.active_sectors?.join(", ") || "");
        setCitiesInput(result.active_cities?.join(", ") || "");
        setTitlesInput(result.active_titles?.join(", ") || "");
        setIntervalInput(result.scrape_interval || 2);
        setLimitInput(result.outreach_limit || 15);
      }
      
      setError(false);
    } catch (err) {
      setError(true);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchChatHistory = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/chat");
      if (response.ok) {
        const result = await response.json();
        setChatHistory(result.history || []);
      }
    } catch (err) {
      console.warn("Could not load chat history gracefully: backend is currently offline.");
    }
  };

  const handleAgentControl = async (
    action: "pause" | "resume" | "scrape_now",
  ) => {
    try {
      setActionError(null);
      setIsActionPending(true);
      const response = await fetch(
        `http://localhost:5000/api/agent/${action}`,
        { method: "POST" },
      );
      if (!response.ok) throw new Error("Backend error");
      fetchDashboard();
    } catch (err) {
      console.warn("Failed to control agent gracefully:", err);
      setActionError("Action failed! Your local backend might be offline or starting.");
      setTimeout(() => setActionError(null), 5000);
    } finally {
      setIsActionPending(false);
    }
  };

  const saveTargetingSettings = async (e: FormEvent) => {
    e.preventDefault();
    try {
      setSaveSuccess(false);
      const formData = new URLSearchParams();
      
      const customSectors = sectorsInput.split(",").map(s => s.strip ? s.strip() : s.trim()).filter(Boolean);
      customSectors.forEach(sector => formData.append("sectors", sector));
      
      formData.append("cities", citiesInput);
      formData.append("titles", titlesInput);
      formData.append("scrape_interval", String(intervalInput));
      formData.append("outreach_limit", String(limitInput));

      const response = await fetch("http://localhost:5000/settings", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });

      if (response.ok) {
        setSaveSuccess(true);
        fetchDashboard();
        setTimeout(() => setSaveSuccess(false), 3000);
      } else {
        throw new Error("Failed to save settings");
      }
    } catch (err) {
      console.warn("Settings error saved gracefully:", err);
      alert("Error saving settings to backend.");
    }
  };

  const handleSendChatMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsg = chatInput.trim();
    setChatInput("");
    setChatLoading(true);

    // Optimistic update
    setChatHistory(prev => [...prev, { role: "user", content: userMsg }]);

    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg })
      });

      if (response.ok) {
        const result = await response.json();
        setChatHistory(result.history || []);
      } else {
        throw new Error("Chat generation failed");
      }
    } catch (err) {
      console.warn("Chat error caught gracefully:", err);
      setChatHistory(prev => [...prev, { role: "assistant", content: "Sorry, I had trouble communicating with my neural model. Please ensure the backend is running." }]);
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 3000); // dynamic status refresh
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div className="bg-[#F8F9FA] min-h-screen w-full flex flex-col p-6 font-sans text-[#1A1A1A]">
      {/* HEADER */}
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <div className="bg-[#E30613] text-white p-2 font-bold text-xl tracking-tighter rounded shadow-sm">
            PRO
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight uppercase flex items-center gap-2">
              Hunter B2B Lead Gen <span className="text-[#E30613] font-black">OS</span>
            </h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">
              Autonomous Intelligence Stack {data?.version === "2.0" ? "• Version 2.0" : "• Loading"}
            </p>
          </div>
        </div>
        
        {/* CONNECTION INDICATOR */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-lg border border-gray-200 shadow-xs">
            <span className="text-[10px] text-gray-400 font-bold uppercase">Backend Status:</span>
            {loading ? (
              <span className="text-xs text-yellow-600 font-medium uppercase flex items-center gap-1">
                <RefreshCw className="w-3 h-3 animate-spin" /> Connecting
              </span>
            ) : error ? (
              <span className="text-xs text-[#E30613] font-medium uppercase flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Offline
              </span>
            ) : (
              <span className="text-xs text-green-600 font-bold uppercase tracking-wider flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Online
              </span>
            )}
          </div>

          {/* TAB SWITCHERS */}
          <div className="flex bg-white rounded-lg p-1 border border-gray-200 shadow-xs">
            <button
              onClick={() => setActiveTab("live")}
              className={`px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-1.5 ${
                activeTab === "live"
                  ? "bg-[#1A1A1A] text-white"
                  : "text-gray-500 hover:text-black"
              }`}
            >
              <Activity className="w-3.5 h-3.5" /> Live Operations
            </button>
            <button
              onClick={() => setActiveTab("targeting")}
              className={`px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-1.5 ${
                activeTab === "targeting"
                  ? "bg-[#1A1A1A] text-white"
                  : "text-gray-500 hover:text-black"
              }`}
            >
              <Sliders className="w-3.5 h-3.5" /> Targeting & AI Chat
            </button>
          </div>
        </div>
      </header>

      {/* OFFLINE SCREEN */}
      {error ? (
        <div className="flex-1 flex flex-col items-center justify-start pt-10 px-4">
          <AlertTriangle className="w-12 h-12 text-[#E30613] mb-4 opacity-50" />
          <h2 className="text-xl font-bold tracking-tighter uppercase mb-2">
            System Offline
          </h2>
          <p className="text-gray-500 max-w-md text-sm text-center mb-8">
            The dashboard cannot connect to your local Hunter Auto agent. Make
            sure you have started it on your Windows machine with your
            downloaded Ollama models.
          </p>

          <div className="w-full max-w-2xl bg-white border border-gray-200 rounded-lg shadow-sm text-left overflow-hidden">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-500">
                Local Docker Startup Guide
              </span>
              <span className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-red-400"></span>
                <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                <span className="w-2 h-2 rounded-full bg-green-400"></span>
              </span>
            </div>
            <div className="p-6 space-y-6 text-sm text-gray-700">
              <div>
                <p className="font-semibold text-black mb-1">
                  1. Download your code
                </p>
                <p className="text-gray-500 text-xs">
                  Click the gear icon (top right) in AI Studio and{" "}
                  <span className="font-bold text-gray-700">Download ZIP</span>,
                  then extract it to a folder.
                </p>
              </div>
              <div>
                <p className="font-semibold text-black mb-1">
                  2. Fill in your API keys
                </p>
                <p className="text-gray-500 text-xs">
                  Inside the extracted folder, rename{" "}
                  <code className="bg-gray-100 text-[#E30613] px-1 rounded">
                    .env.example
                  </code>{" "}
                  to{" "}
                  <code className="bg-gray-100 text-[#E30613] px-1 rounded">
                    .env
                  </code>{" "}
                  and fill in your Gmail App Password, Google Sheets ID, and
                  Hunter.io API key.
                </p>
              </div>
              <div>
                <p className="font-semibold text-black mb-1">
                  3. Start the Docker containers
                </p>
                <div className="bg-[#1A1A1A] text-green-400 p-3 rounded font-mono text-xs">
                  $ docker compose up -d --build
                </div>
                <p className="text-gray-500 text-xs mt-2 italic flex items-center gap-1">
                  <RefreshCw className="w-3 h-3 animate-spin" /> Once running,
                  this dashboard will automatically come online!
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* STATS STRIP */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Total Scraped Leads
              </div>
              <div className="text-3xl font-light leading-none text-[#1A1A1A]">
                {data?.stats?.total || 0}
              </div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Outreach Attempts Today
              </div>
              <div className="text-3xl font-light leading-none text-[#1A1A1A]">
                {data?.stats?.sent_today || 0}
              </div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Response Rate
              </div>
              <div className="text-3xl font-light leading-none text-green-600">
                {data?.stats?.response_rate || "0%"}
              </div>
            </div>
            <div className="bg-white p-5 border border-[#E30613]/20 border-l-4 border-l-[#E30613] rounded shadow-sm">
              <div className="text-[10px] text-[#E30613] font-bold uppercase mb-1">
                Meetings Booked
              </div>
              <div className="text-3xl font-semibold leading-none text-[#E30613]">
                {data?.stats?.meetings || 0}
              </div>
            </div>
          </div>

          {/* ACTIVE TAB 1: LIVE OPERATIONS */}
          {activeTab === "live" && (
            <div className="space-y-6">
              {/* REAL-TIME SCRAPING ACTIVITY WIDGET */}
              <div className="bg-white border border-gray-200 p-5 rounded shadow-sm">
                <div className="flex justify-between items-center border-b border-gray-100 pb-3 mb-4">
                  <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${data?.status_info?.is_scraping ? 'bg-green-400' : 'bg-gray-400'}`}></span>
                      <span className={`relative inline-flex rounded-full h-2 w-2 ${data?.status_info?.is_scraping ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                    </span>
                    <h3 className="text-xs font-bold uppercase tracking-widest text-[#1A1A1A]">
                      Real-Time Scraping Activity Feed
                    </h3>
                  </div>
                  <span className="text-[10px] text-gray-400 font-mono">Status updates on maps & linkedin</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-sm">
                  <div className="bg-gray-50 p-3 rounded border border-gray-100">
                    <div className="text-[10px] text-gray-400 uppercase font-bold mb-1">Engine State</div>
                    <div className="font-semibold flex items-center gap-1.5">
                      {data?.status_info?.is_scraping ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Scraping Active
                        </span>
                      ) : (
                        <span className="text-gray-500">Idle Waiting</span>
                      )}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded border border-gray-100 md:col-span-2">
                    <div className="text-[10px] text-gray-400 uppercase font-bold mb-1">Current Activity</div>
                    <div className="font-medium text-gray-700 truncate" title={data?.status_info?.current_activity}>
                      {data?.status_info?.current_activity || "Idle - Ready for manual or scheduled launch"}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded border border-gray-100">
                    <div className="text-[10px] text-gray-400 uppercase font-bold mb-1">Last Scraped Target</div>
                    <div className="font-semibold text-gray-800 flex items-center gap-1.5">
                      <span className="truncate">{data?.status_info?.last_scraped_company || "-"}</span>
                      {data?.status_info?.last_scraped_source && (
                        <span className="text-[8px] bg-indigo-100 text-indigo-700 font-bold px-1 rounded uppercase">
                          {data?.status_info?.last_scraped_source}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Last Found Leads Carousel strip */}
                {data?.status_info?.recent_scraped_leads?.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <div className="text-[10px] text-gray-400 uppercase font-bold mb-2">Recently Scraped Real-Time Streams:</div>
                    <div className="flex gap-3 overflow-x-auto pb-1">
                      {data.status_info.recent_scraped_leads.map((lead: any, idx: number) => (
                        <div key={idx} className="bg-blue-50/50 border border-blue-100 px-3 py-1.5 rounded-md text-xs shrink-0 flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-blue-500" />
                          <span className="font-bold text-blue-900">{lead.Company}</span>
                          <span className="text-blue-500 text-[10px] font-mono">({lead.Source})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* TWO PANEL ACTIVITY & LOGS VIEW */}
              <div className="flex gap-6 flex-1 min-h-[500px]">
                {/* Main Table */}
                <main className="flex-1 bg-white border border-gray-200 rounded overflow-hidden flex flex-col shadow-sm">
                  <div className="p-4 bg-gray-50 flex justify-between items-center border-b border-gray-200">
                    <h2 className="text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                      Recent Activity Queue
                    </h2>
                    <div className="flex gap-2">
                      {data?.agent_state === "paused" ? (
                        <button
                          disabled={isActionPending}
                          onClick={() => handleAgentControl("resume")}
                          className="text-[10px] disabled:opacity-50 font-bold uppercase bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded transition-colors"
                        >
                          {isActionPending ? "..." : "Resume Agent"}
                        </button>
                      ) : (
                        <button
                          disabled={isActionPending}
                          onClick={() => handleAgentControl("pause")}
                          className="text-[10px] disabled:opacity-50 font-bold uppercase bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded transition-colors"
                        >
                          {isActionPending ? "..." : "Pause Agent"}
                        </button>
                      )}
                      <button
                        disabled={isActionPending}
                        onClick={() => handleAgentControl("scrape_now")}
                        className="text-[10px] disabled:opacity-50 font-bold uppercase bg-[#E30613] hover:bg-red-700 text-white px-3 py-1 rounded transition-colors shadow-sm ml-2"
                      >
                        {isActionPending ? "..." : "Start Scrape Now"}
                      </button>
                    </div>
                  </div>
                  {actionError && (
                    <div className="bg-red-50 border-b border-red-200 p-3 text-xs text-red-600 font-medium">
                      ⚠️ {actionError}
                    </div>
                  )}
                  <div className="flex-1 overflow-auto">
                    <table className="w-full text-left">
                      <thead className="text-[10px] uppercase tracking-wider font-bold text-gray-400 bg-gray-50/50 sticky top-0">
                        <tr>
                          <th className="px-6 py-3 border-b border-gray-100">
                            Company / Location
                          </th>
                          <th className="px-6 py-3 border-b border-gray-100 text-center">
                            Score
                          </th>
                          <th className="px-6 py-3 border-b border-gray-100">
                            Source
                          </th>
                          <th className="px-6 py-3 border-b border-gray-100">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {(data?.recent || []).length === 0 ? (
                          <tr>
                            <td
                              colSpan={4}
                              className="px-6 py-8 text-center text-gray-400 text-sm"
                            >
                              No recent leads processed yet. Check your local logs or start scraping.
                            </td>
                          </tr>
                        ) : (
                          (data?.recent || []).map((lead: any, i: number) => (
                            <tr
                              key={i}
                              className="hover:bg-gray-50 transition-colors"
                            >
                              <td className="px-6 py-4">
                                <div className="text-xs font-bold text-gray-900">
                                  {lead.Company}
                                </div>
                                <div className="text-[10px] text-gray-400 uppercase">
                                  {lead.Name || "-"} • {lead.Title || "-"}
                                </div>
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span
                                  className={`text-xs font-bold px-2 py-1 rounded ${Number(lead.Score) >= 7 ? "bg-green-50 text-green-600 border border-green-200" : "bg-gray-50 text-gray-400"}`}
                                >
                                  {lead.Score || "-"}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded uppercase">
                                  {lead.Source}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <span className={`text-[10px] font-bold px-2.5 py-1 rounded uppercase tracking-tighter border ${
                                  lead.Status === "meeting_booked" ? "bg-green-50 text-green-700 border-green-200" :
                                  lead.Status === "not_interested" ? "bg-gray-100 text-gray-500 border-gray-200" :
                                  "bg-red-50 text-[#E30613] border-red-100"
                                }`}>
                                  {lead.Status}
                                </span>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </main>

                {/* Sidebar Logs */}
                <aside className="w-80 flex flex-col gap-6">
                  {/* CONFIGURATION SUMMARY SUMMARY WIDGET */}
                  <div className="bg-white border border-gray-200 p-5 rounded shadow-sm flex flex-col h-[200px]">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-[#1A1A1A]">
                        Active Campaign Summary
                      </h3>
                      <span className="text-[8px] bg-green-100 text-green-700 font-bold px-1.5 py-0.5 rounded uppercase font-mono">
                        Active
                      </span>
                    </div>
                    <div className="space-y-2 overflow-y-auto flex-1 text-[11px] text-gray-600">
                      <div>
                        <strong>Cities:</strong> <span className="text-gray-900">{data?.active_cities?.join(", ") || "None"}</span>
                      </div>
                      <div>
                        <strong>Sectors:</strong> <span className="text-gray-900">{data?.active_sectors?.join(", ") || "None"}</span>
                      </div>
                      <div>
                        <strong>Titles:</strong> <span className="text-gray-900">{data?.active_titles?.join(", ") || "None"}</span>
                      </div>
                      <div className="flex justify-between text-[10px] text-gray-400 font-mono mt-2 pt-2 border-t border-gray-100">
                        <span>Limit: {data?.outreach_limit} / day</span>
                        <span>Interval: {data?.scrape_interval} hrs</span>
                      </div>
                    </div>
                  </div>

                  {/* Logs Container */}
                  <div className="bg-[#1A1A1A] border border-gray-800 text-green-400 p-4 rounded flex flex-col flex-1 shadow-sm overflow-hidden h-[300px]">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        System CLI Logs
                      </h3>
                      <span className="flex items-center gap-1 text-[8px] text-gray-500 uppercase tracking-widest border border-gray-700 px-1 py-0.5 rounded">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Streaming
                      </span>
                    </div>
                    <div className="font-mono text-[10px] space-y-1 overflow-y-auto flex-1 pr-2 pb-2 leading-relaxed">
                      {(data?.logs || []).length === 0 ? (
                        <div className="text-gray-600 italic">
                          No logging outputs yet...
                        </div>
                      ) : (
                        (data?.logs || []).map((log: string, i: number) => (
                          <div key={i} className="whitespace-pre-wrap break-words border-b border-gray-900/50 pb-1 text-gray-300">
                            {log}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </aside>
              </div>
            </div>
          )}

          {/* ACTIVE TAB 2: TARGETING & AI ASSISTANT */}
          {activeTab === "targeting" && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              
              {/* TARGETING CONFIGURATION EDITOR PANEL (LEFT - 5 cols) */}
              <div className="lg:col-span-5 bg-white border border-gray-200 p-6 rounded shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <Sliders className="w-5 h-5 text-[#E30613]" />
                  <h2 className="text-sm font-bold uppercase tracking-wider text-[#1A1A1A]">Targeting Variables Control Panel</h2>
                </div>
                <p className="text-xs text-gray-500 mb-6">
                  Customize the areas, job roles, industries, and scheduling parameters. Pressing save will hot-reload settings instantly across scrapers.
                </p>

                {saveSuccess && (
                  <div className="bg-green-50 border border-green-200 text-green-800 p-3 text-xs font-bold rounded mb-4 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" /> Settings updated successfully!
                  </div>
                )}

                <form onSubmit={saveTargetingSettings} className="space-y-4 text-xs">
                  <div>
                    <label className="block font-bold text-gray-700 mb-1 uppercase tracking-widest text-[9px]">Target Cities / Zones</label>
                    <input 
                      type="text" 
                      value={citiesInput} 
                      onChange={(e) => setCitiesInput(e.target.value)}
                      placeholder="e.g. Tunis, Sousse, Sfax, Ariana"
                      className="w-full p-2.5 border border-gray-300 rounded focus:border-[#E30613] outline-none"
                      required
                    />
                    <p className="text-[10px] text-gray-400 mt-1">Comma-separated list of target cities in Tunisia.</p>
                  </div>

                  <div>
                    <label className="block font-bold text-gray-700 mb-1 uppercase tracking-widest text-[9px]">Target Job Titles (LinkedIn)</label>
                    <input 
                      type="text" 
                      value={titlesInput} 
                      onChange={(e) => setTitlesInput(e.target.value)}
                      placeholder="e.g. Directeur Général, CEO, Gérant, Fondateur"
                      className="w-full p-2.5 border border-gray-300 rounded focus:border-[#E30613] outline-none"
                      required
                    />
                    <p className="text-[10px] text-gray-400 mt-1">Comma-separated role keywords searched on LinkedIn.</p>
                  </div>

                  <div>
                    <label className="block font-bold text-gray-700 mb-1 uppercase tracking-widest text-[9px]">Target Industries / Sectors</label>
                    <input 
                      type="text" 
                      value={sectorsInput} 
                      onChange={(e) => setSectorsInput(e.target.value)}
                      placeholder="e.g. IT, Banque, Industrie, Commerce, Santé"
                      className="w-full p-2.5 border border-gray-300 rounded focus:border-[#E30613] outline-none"
                      required
                    />
                    <p className="text-[10px] text-gray-400 mt-1">Industries used for search queries on Maps & LinkedIn.</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block font-bold text-gray-700 mb-1 uppercase tracking-widest text-[9px]">Scrape Interval (Hrs)</label>
                      <input 
                        type="number" 
                        value={intervalInput} 
                        onChange={(e) => setIntervalInput(Number(e.target.value))}
                        className="w-full p-2.5 border border-gray-300 rounded focus:border-[#E30613] outline-none"
                        min="1"
                        required
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-gray-700 mb-1 uppercase tracking-widest text-[9px]">Daily Limit (Leads)</label>
                      <input 
                        type="number" 
                        value={limitInput} 
                        onChange={(e) => setLimitInput(Number(e.target.value))}
                        className="w-full p-2.5 border border-gray-300 rounded focus:border-[#E30613] outline-none"
                        min="1"
                        required
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    className="w-full bg-[#1A1A1A] hover:bg-black text-white py-3 rounded font-bold uppercase tracking-wider text-xs shadow transition-all mt-4"
                  >
                    Save & Update Campaign Configuration
                  </button>
                </form>
              </div>

              {/* INTERACTIVE AI MESSENGER WITH MEMORY PANEL (RIGHT - 7 cols) */}
              <div className="lg:col-span-7 bg-white border border-gray-200 rounded shadow-sm flex flex-col h-[520px]">
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-indigo-600" />
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">Hunter AI Strategic Assistant</h3>
                      <p className="text-[9px] text-gray-400 font-semibold uppercase">Persistent memory active • Autonomy integration</p>
                    </div>
                  </div>
                  <span className="text-[8px] bg-indigo-100 text-indigo-700 font-bold px-1.5 py-0.5 rounded uppercase">Memory Link</span>
                </div>

                {/* Chat window */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
                  {chatHistory.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-400">
                      <Bot className="w-10 h-10 mb-2 opacity-30 text-indigo-600" />
                      <p className="text-xs font-semibold uppercase tracking-wider mb-1">Talk with Hermes</p>
                      <p className="text-[11px] max-w-xs text-gray-400">
                        Ask me to draft email sequences, score lead suitability, customize target pitches, or save custom system instructions in memory.
                      </p>
                    </div>
                  ) : (
                    chatHistory.map((msg, idx) => (
                      <div 
                        key={idx} 
                        className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                      >
                        <div className={`p-2 rounded-lg text-xs leading-relaxed ${
                          msg.role === 'user' 
                            ? 'bg-[#1A1A1A] text-white rounded-br-none' 
                            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-xs'
                        }`}>
                          <div className="text-[8px] opacity-40 font-bold uppercase mb-1">
                            {msg.role === 'user' ? 'You' : 'Hermes Agent'}
                          </div>
                          <div className="whitespace-pre-wrap">{msg.content}</div>
                        </div>
                      </div>
                    ))
                  )}
                  {chatLoading && (
                    <div className="flex gap-3 mr-auto items-center text-xs text-gray-500 italic bg-white border border-gray-200 p-2.5 rounded-lg shadow-xs">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-600" /> Hermes is thinking and consulting memory...
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input window */}
                <form onSubmit={handleSendChatMessage} className="p-3 border-t border-gray-100 bg-white flex gap-2">
                  <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask Hermes to optimize criteria or analyze campaigns..."
                    className="flex-1 p-2.5 border border-gray-300 rounded focus:border-indigo-500 text-xs outline-none"
                    disabled={chatLoading}
                  />
                  <button 
                    type="submit"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 rounded flex items-center justify-center transition-colors shadow-xs disabled:opacity-50"
                    disabled={chatLoading || !chatInput.trim()}
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>

            </div>
          )}
        </>
      )}
    </div>
  );
}
