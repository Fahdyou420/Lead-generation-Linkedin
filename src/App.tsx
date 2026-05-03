/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useState } from 'react';
import { Bot, RefreshCw, AlertTriangle } from 'lucide-react';

export default function App() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchDashboard = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dashboard');
      if (!response.ok) throw new Error('Network response was not ok');
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

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#F5F5F5] min-h-screen w-full overflow-y-auto flex flex-col p-6 font-sans text-[#1A1A1A]">
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <div className="bg-[#E30613] text-white p-2 font-bold text-xl tracking-tighter rounded">H1.0</div>
          <div>
            <h1 className="text-xl font-bold tracking-tight uppercase">Hunter Auto <span className="text-[#E30613]">Pro</span></h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">Autonomous Ooredoo B2B Agent • Tunisia</p>
          </div>
        </div>
        <div className="flex items-center gap-8">
          <div className="flex gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-400 font-bold uppercase">Local Backend</span>
              {loading ? (
                <span className="text-xs text-yellow-600 font-medium uppercase flex items-center gap-1">
                   <RefreshCw className="w-3 h-3 animate-spin"/> Connecting...
                </span>
              ) : error ? (
                <span className="text-xs text-[#E30613] font-medium uppercase flex items-center gap-1">
                   <AlertTriangle className="w-3 h-3"/> Offline
                </span>
              ) : (
                <span className="text-xs text-green-600 font-medium uppercase tracking-wider flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span> Online
                </span>
              )}
            </div>
            <div className="flex flex-col items-end border-l pl-4 border-gray-300">
              <span className="text-[10px] text-gray-400 font-bold uppercase">DB State</span>
              <span className={`text-xs ${error ? 'text-gray-400' : 'text-green-600'} font-medium uppercase tracking-wider flex items-center gap-1`}>
                <span className={`w-2 h-2 rounded-full ${error ? 'bg-gray-300' : 'bg-green-500'}`}></span> Sheets Sync
              </span>
            </div>
          </div>
        </div>
      </header>

      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-10 mt-10">
          <AlertTriangle className="w-16 h-16 text-[#E30613] mb-4 opacity-50" />
          <h2 className="text-2xl font-bold tracking-tighter uppercase mb-2">System Offline</h2>
          <p className="text-gray-500 max-w-md text-sm mb-6">
            The dashboard cannot connect to your local Hunter Auto agent. Make sure you have started it with <code className="bg-gray-200 px-1 rounded">docker compose up -d</code> on your machine.
          </p>
          <p className="text-xs text-gray-400 font-medium uppercase tracking-wider">
            Waiting for connection on http://localhost:5000 ...
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Total Scraped</div>
              <div className="text-3xl font-light leading-none">{data?.stats?.total || 0}</div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Active Outreach</div>
              <div className="text-3xl font-light leading-none">{data?.stats?.sent_today || 0}</div>
            </div>
            <div className="bg-white p-5 border border-gray-200 rounded shadow-sm">
              <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Response Rate</div>
              <div className="text-3xl font-light leading-none">{data?.stats?.response_rate || "0%"}</div>
            </div>
            <div className="bg-white p-5 border border-[#E30613]/20 border-l-4 border-l-[#E30613] rounded shadow-sm">
              <div className="text-[10px] text-[#E30613] font-bold uppercase mb-1">Meetings Booked</div>
              <div className="text-3xl font-light leading-none">{data?.stats?.meetings || 0}</div>
            </div>
          </div>

          <div className="flex gap-6 flex-1 overflow-hidden min-h-[500px]">
             {/* Main Table */}
             <main className="flex-1 bg-white border border-gray-200 rounded overflow-hidden flex flex-col shadow-sm">
              <div className="p-4 border-bottom bg-gray-50 flex justify-between items-center border-b border-gray-200">
                <h2 className="text-xs font-bold uppercase tracking-widest">Recent Activity Queue</h2>
                <div className="flex gap-2">
                  <span className="text-[10px] uppercase font-bold text-gray-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-[#E30613] animate-pulse rounded-full"></span> Live Updates
                  </span>
                </div>
              </div>
              <div className="flex-1 overflow-auto">
                <table className="w-full text-left">
                  <thead className="text-[10px] uppercase tracking-wider font-bold text-gray-400 bg-gray-50/50 sticky top-0">
                    <tr>
                      <th className="px-6 py-3 border-b border-gray-100">Company</th>
                      <th className="px-6 py-3 border-b border-gray-100 text-center">Score</th>
                      <th className="px-6 py-3 border-b border-gray-100">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {(data?.recent || []).length === 0 ? (
                      <tr>
                        <td colSpan={3} className="px-6 py-8 text-center text-gray-400 text-sm">
                          No recent leads processed yet. Check your local logs.
                        </td>
                      </tr>
                    ) : (data?.recent || []).map((lead: any, i: number) => (
                       <tr key={i} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="text-xs font-bold">{lead.Company}</div>
                          <div className="text-[10px] text-gray-400 uppercase">{lead.Name || '-'} • {lead.Title || lead.Source}</div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`text-xs font-bold px-2 py-1 rounded ${Number(lead.Score) >= 7 ? 'bg-green-50 text-green-600' : 'bg-gray-50 text-gray-400'}`}>
                            {lead.Score || '-'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-[10px] font-bold text-[#E30613] bg-[#E30613]/5 px-2 py-1 rounded uppercase tracking-tighter">
                            {lead.Status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </main>

            <aside className="w-64 flex flex-col gap-6">
              <div className="bg-[#1A1A1A] text-white p-5 rounded h-1/2 flex flex-col">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-4">Active Sectors</h3>
                <div className="space-y-3 overflow-y-auto flex-1 pr-2">
                   {(data?.active_sectors || []).map((sector: string, i: number) => (
                     <div key={i} className="flex items-center justify-between text-xs">
                       <span className="flex items-center gap-2">
                         <span className="w-1.5 h-1.5 bg-[#E30613] rounded-full"></span> {sector}
                       </span>
                     </div>
                   ))}
                </div>
              </div>
            </aside>
          </div>
        </>
      )}
    </div>
  );
}
