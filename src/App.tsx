/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useState } from "react";
import { Bot, RefreshCw, AlertTriangle } from "lucide-react";

export default function App() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isActionPending, setIsActionPending] = useState<boolean>(false);

  const fetchDashboard = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/dashboard");
      if (!response.ok) throw new Error("Network response was not ok");
      const result = await response.json();
      setData(result);
      setError(false);
    } catch (err) {
      setError(true);
      setData(null);
    } finally {
      setLoading(false);
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
      if (!response.ok) {
        throw new Error("Old backend");
      }
      fetchDashboard();
    } catch (err) {
      console.error("Failed to control agent", err);
      setActionError(
        "Action failed! Your local Docker backend is outdated. Please re-download the ZIP and rebuild Docker to get the new capabilities.",
      );
      setTimeout(() => setActionError(null), 8000);
    } finally {
      setIsActionPending(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 3000); // refresh every 3s for real-time logs
    return () => clearInterval(interval);
  }, []);

  const needsBackendUpdate =
    data && data.status === "online" && data.agent_state === undefined;

  return (
    <div className="bg-[#F5F5F5] min-h-screen w-full overflow-y-auto flex flex-col p-6 font-sans text-[#1A1A1A]">
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <div className="bg-[#E30613] text-white p-2 font-bold text-xl tracking-tighter rounded">
            H1.0
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight uppercase">
              Hunter Auto <span className="text-[#E30613]">Pro</span>
            </h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">
              Autonomous Ooredoo B2B Agent{" "}
              {data?.version === "2.0" ? "• V2.0 Active" : "• Tunisia"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-8">
          <div className="flex gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-400 font-bold uppercase">
                Local Backend
              </span>
              {loading ? (
                <span className="text-xs text-yellow-600 font-medium uppercase flex items-center gap-1">
                  <RefreshCw className="w-3 h-3 animate-spin" /> Connecting...
                </span>
              ) : error ? (
                <span className="text-xs text-[#E30613] font-medium uppercase flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Offline
                </span>
              ) : (
                <span className="text-xs text-green-600 font-medium uppercase tracking-wider flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>{" "}
                  Online
                </span>
              )}
            </div>
            <div className="flex flex-col items-end border-l pl-4 border-gray-300">
              <span className="text-[10px] text-gray-400 font-bold uppercase">
                DB State
              </span>
              <span
                className={`text-xs ${error ? "text-gray-400" : "text-green-600"} font-medium uppercase tracking-wider flex items-center gap-1`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${error ? "bg-gray-300" : "bg-green-500"}`}
                ></span>{" "}
                Sheets Sync
              </span>
            </div>
          </div>
        </div>
      </header>

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
                  3. Authenticate LinkedIn
                </p>
                <p className="text-gray-500 text-xs mb-2">
                  Open Command Prompt (`cmd`) in your folder and run this to
                  save your session so the bot doesn't get blocked:
                </p>
                <div className="bg-[#1A1A1A] text-gray-300 p-3 rounded font-mono text-[10px] overflow-x-auto whitespace-pre">
                  <span className="text-blue-400">pip</span> install playwright
                  <br />
                  <span className="text-blue-400">playwright</span> install
                  chromium
                  <br />
                  <span className="text-blue-400">python</span> -c "from
                  playwright.sync_api import sync_playwright;
                  p=sync_playwright().start();
                  browser=p.chromium.launch(headless=False);
                  context=browser.new_context(); page=context.new_page();
                  page.goto('https://www.linkedin.com/login');
                  print('\n&gt;&gt;&gt; LOGIN IN BROWSER NOW (60s)
                  &lt;&lt;&lt;\n'); page.wait_for_timeout(60000);
                  context.storage_state(path='playwright_sessions/state.json');
                  browser.close(); p.stop()"
                </div>
              </div>
              <div>
                <p className="font-semibold text-black mb-1">
                  4. Start the Docker containers
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

          <div className="w-full max-w-2xl bg-white border border-gray-200 rounded-lg shadow-sm text-left overflow-hidden mt-6 mb-10">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 flex justify-between items-center">
              <span className="text-xs font-bold uppercase tracking-widest text-[#E30613]">
                FAQ & Customization
              </span>
              <span className="bg-green-100 text-green-700 font-bold text-[10px] px-2 py-0.5 rounded uppercase font-mono border border-green-200">
                Agent Setup
              </span>
            </div>
            <div className="p-6 space-y-4 text-sm text-gray-700">
              <div>
                <p className="font-semibold text-black mb-1">
                  How do I add more context/data for the AI to pitch better?
                </p>
                <p className="text-gray-500 text-xs mb-3">
                  You can dynamically update the AI's "brain" and knowledge base
                  at runtime using the newly added Agent Skills file:
                </p>

                <div className="border border-indigo-100 bg-indigo-50/50 rounded-lg p-4 mb-3">
                  <div className="font-mono text-xs font-bold text-indigo-700 mb-2 flex items-center gap-2">
                    <span className="bg-indigo-100 px-1 rounded border border-indigo-200">
                      📄 hunter_auto/knowledge/skills.md
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-600 mb-2">
                    This markdown file acts as the AI's core instructions. The
                    system reads it automatically before every interaction. You
                    can paste:
                  </p>
                  <ul className="text-[11px] text-gray-600 space-y-1 list-disc pl-4">
                    <li>
                      Your exact Ooredoo B2B pricing guidelines or constraints.
                    </li>
                    <li>Your Ideal Customer Profile (ICP) for lead scoring.</li>
                    <li>
                      Your preferred tone of voice or cultural business
                      etiquette.
                    </li>
                    <li>Key value propositions (e.g., Fibre Optique Pro).</li>
                  </ul>
                </div>

                <p className="text-green-700 text-xs font-medium bg-green-50 px-2 py-1.5 rounded inline-block border border-green-100">
                  ✨ Hot Reloading Active: You do NOT need to restart Docker.
                  Just edit the `skills.md` file and save it on your machine!
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          {needsBackendUpdate && (
            <div className="bg-[#E30613]/10 border border-[#E30613]/20 text-[#E30613] p-4 rounded mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="font-bold uppercase tracking-widest text-xs mb-1">
                  Action Required: Update Local Backend
                </h3>
                <p className="text-[11px] text-gray-700 max-w-lg">
                  You are viewing the{" "}
                  <strong className="font-bold">v2.0 dashboard</strong>, but
                  your container running on{" "}
                  <strong className="font-mono bg-red-100 text-red-800 px-1 rounded">
                    localhost:5000
                  </strong>{" "}
                  is an older version. It seems your{" "}
                  <strong className="font-mono bg-red-100 text-red-800 px-1 rounded">
                    docker compose build
                  </strong>{" "}
                  was run in a folder with an old{" "}
                  <strong className="font-mono bg-red-100 text-red-800 px-1 rounded">
                    Dockerfile
                  </strong>
                  , or the ZIP wasn't correctly extracted.
                </p>
              </div>
              <div className="shrink-0 bg-white p-3 rounded border border-[#E30613]/20 text-[10px] font-mono text-[#E30613] shadow-sm leading-relaxed">
                1. Export latest ZIP from AI Studio
                <br />
                2. Extract it to a new folder
                <br />
                3. Open the folder `hunter_auto` inside the extracted files
                <br />
                4. Verify `Dockerfile` is right there!
                <br />
                5. docker compose down -v
                <br />
                6. docker compose up -d --build
              </div>
            </div>
          )}

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Total Scraped
              </div>
              <div className="text-3xl font-light leading-none">
                {data?.stats?.total || 0}
              </div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Active Outreach
              </div>
              <div className="text-3xl font-light leading-none">
                {data?.stats?.sent_today || 0}
              </div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">
                Response Rate
              </div>
              <div className="text-3xl font-light leading-none">
                {data?.stats?.response_rate || "0%"}
              </div>
            </div>
            <div className="bg-white p-5 border border-[#E30613]/20 border-l-4 border-l-[#E30613] rounded shadow-sm">
              <div className="text-[10px] text-[#E30613] font-bold uppercase mb-1">
                Meetings Booked
              </div>
              <div className="text-3xl font-light leading-none">
                {data?.stats?.meetings || 0}
              </div>
            </div>
          </div>

          <div className="flex gap-6 flex-1 overflow-hidden min-h-[500px]">
            {/* Main Table */}
            <main className="flex-1 bg-white border border-gray-200 rounded overflow-hidden flex flex-col shadow-sm">
              <div className="p-4 border-bottom bg-gray-50 flex justify-between items-center border-b border-gray-200">
                <h2 className="text-xs font-bold uppercase tracking-widest">
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
                        Company
                      </th>
                      <th className="px-6 py-3 border-b border-gray-100 text-center">
                        Score
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
                          colSpan={3}
                          className="px-6 py-8 text-center text-gray-400 text-sm"
                        >
                          No recent leads processed yet. Check your local logs.
                        </td>
                      </tr>
                    ) : (
                      (data?.recent || []).map((lead: any, i: number) => (
                        <tr
                          key={i}
                          className="hover:bg-gray-50 transition-colors"
                        >
                          <td className="px-6 py-4">
                            <div className="text-xs font-bold">
                              {lead.Company}
                            </div>
                            <div className="text-[10px] text-gray-400 uppercase">
                              {lead.Name || "-"} • {lead.Title || lead.Source}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span
                              className={`text-xs font-bold px-2 py-1 rounded ${Number(lead.Score) >= 7 ? "bg-green-50 text-green-600" : "bg-gray-50 text-gray-400"}`}
                            >
                              {lead.Score || "-"}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-[10px] font-bold text-[#E30613] bg-[#E30613]/5 px-2 py-1 rounded uppercase tracking-tighter">
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

            <aside className="w-80 flex flex-col gap-6">
              <div className="bg-white border border-gray-200 p-5 rounded flex flex-col h-1/3 shadow-sm">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-[#1A1A1A] mb-4">
                  Active Sectors
                </h3>
                <div className="space-y-3 overflow-y-auto flex-1 pr-2">
                  {(data?.active_sectors || []).map(
                    (sector: string, i: number) => (
                      <div
                        key={i}
                        className="flex items-center justify-between text-xs"
                      >
                        <span className="flex items-center gap-2 text-gray-700">
                          <span className="w-1.5 h-1.5 bg-[#E30613] rounded-full"></span>{" "}
                          {sector}
                        </span>
                      </div>
                    ),
                  )}
                </div>
              </div>

              <div className="bg-[#1A1A1A] border border-gray-800 text-green-400 p-4 rounded flex flex-col flex-1 shadow-sm overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    Real-Time Workflow
                  </h3>
                  <span className="flex items-center gap-1 text-[8px] text-gray-500 uppercase tracking-widest border border-gray-700 px-1 py-0.5 rounded">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>{" "}
                    Streaming
                  </span>
                </div>
                <div className="font-mono text-[10px] space-y-1 overflow-y-auto flex-1 pr-2 pb-2 leading-relaxed">
                  {(data?.logs || []).length === 0 ? (
                    <div className="text-gray-600 italic">
                      No logs available yet...
                    </div>
                  ) : (
                    (data?.logs || []).map((log: string, i: number) => (
                      <div key={i} className="whitespace-pre-wrap break-words">
                        {log}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </aside>
          </div>
        </>
      )}
    </div>
  );
}
