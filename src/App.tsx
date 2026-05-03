/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Download, Terminal, Database, Bot, Github, Share, Settings } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  return (
    <div className="min-h-screen bg-[#F5F5F5] flex flex-col items-center justify-center p-6 font-sans text-[#1A1A1A]">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl w-full flex flex-col gap-6"
      >
        <header className="flex justify-between items-center bg-white p-5 border border-gray-200 rounded shadow-sm">
          <div className="flex items-center gap-4">
            <div className="bg-[#E30613] text-white p-2 font-bold text-xl tracking-tighter rounded flex items-center justify-center">
              <Bot size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight uppercase">Hunter Auto <span className="text-[#E30613]">1.0 Generated</span></h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">Autonomous Ooredoo B2B Agent • Tunisia</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex flex-col items-end border-gray-300">
                <span className="text-[10px] text-gray-400 font-bold uppercase">Status</span>
                <span className="text-xs text-green-600 font-medium uppercase tracking-wider flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500"></span> Generated
                </span>
            </div>
          </div>
        </header>
        
        <div className="bg-white border border-gray-200 rounded overflow-hidden flex flex-col shadow-sm">
          <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
             <div className="flex items-center gap-3">
               <span className="w-2 h-2 bg-green-500 rounded-full"></span>
               <h2 className="text-xs font-bold uppercase tracking-widest text-[#1A1A1A]">Code Generation Complete</h2>
             </div>
          </div>
          
          <div className="p-6">
            <p className="text-[11px] font-mono text-gray-600 mb-6 max-w-2xl leading-relaxed">
              Because <strong className="text-[#1A1A1A]">Hunter Auto 1.0</strong> is a specialized Python automation suite using Playwright, local Ollama models, and Docker Compose, it cannot run directly inside this React/Node.js web preview sandbox. You need to export it and run it locally.
            </p>

            <div className="flex flex-col gap-4 mb-6">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Export &amp; Run Strategy</h3>
              
              <div className="bg-white p-5 border border-[#E30613]/20 border-l-4 border-l-[#E30613] rounded shadow-sm flex items-start gap-4">
                <div className="bg-gray-50 p-2 border border-gray-100 rounded">
                   <Terminal className="w-5 h-5 text-[#E30613]" />
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-widest mb-1">1. Export the Codebase</h4>
                  <p className="text-[11px] text-gray-500 font-medium">
                    Click the <strong className="text-[#1A1A1A]">Settings</strong> menu <Settings className="inline w-3 h-3 text-gray-400"/> (gear icon) in AI Studio and select <strong className="text-[#1A1A1A]">Download ZIP</strong> or <strong className="text-[#1A1A1A]">Export to GitHub</strong>.
                  </p>
                </div>
              </div>

              <div className="bg-white p-5 border border-gray-200 rounded shadow-sm flex items-start gap-4">
                <div className="bg-gray-50 p-2 border border-gray-100 rounded">
                   <Database className="w-5 h-5 text-[#1A1A1A]" />
                </div>
                <div className="w-full">
                  <h4 className="text-xs font-bold uppercase tracking-widest mb-2">2. Run Locally via Docker</h4>
                  <p className="text-[11px] text-gray-500 font-medium mb-3">
                    Extract the ZIP, open your terminal in the extracted folder, and execute:
                  </p>
                  <code className="bg-[#1A1A1A] text-gray-300 px-4 py-3 rounded text-[11px] block font-mono w-full">
                    <span className="text-[#E30613]">$</span> cd hunter_auto <br/>
                    <span className="text-[#E30613]">$</span> docker-compose up -d --build
                  </code>
                </div>
              </div>
              
            </div>
            
            <div className="text-[10px] text-gray-500 uppercase tracking-wider font-bold pt-4 border-t border-gray-100 flex items-center gap-2 mt-2">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
              Note: Check the hunter_auto/README.md file in your exported ZIP for required configuration steps like Google Sheets credentials and LinkedIn session cookies.
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
