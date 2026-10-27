import React, { useState } from 'react';

const Intake = () => {
  const [selectedOption, setSelectedOption] = useState(3);

  const options = [
    "Never",
    "Rarely (1-2 days)",
    "Several days (3-7 days)",
    "More than half the days",
    "Nearly every day"
  ];

  return (
    <div className="flex h-full w-full bg-[#0a0a0a]">
      {/* Center Content Area */}
      <div className="flex-1 flex flex-col h-full border-r border-[#272A30] overflow-y-auto p-8">
        
        <div className="max-w-[800px] w-full mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <div className="flex justify-between items-end mb-4">
              <div>
                <div className="text-[#8c909f] font-mono text-[11px] uppercase tracking-wider mb-2">CARDIOVASCULAR BASELINE</div>
                <h2 className="text-[#4d8eff] text-[15px] font-medium">Section 2: Symptom Frequency</h2>
              </div>
              <div className="text-[#8c909f] font-mono text-[12px]">
                Question 4 of 12
              </div>
            </div>
            {/* Progress Bar */}
            <div className="h-[2px] w-full bg-[#272A30] rounded-full overflow-hidden flex">
              <div className="h-full bg-[#4d8eff] w-1/3"></div>
            </div>
          </div>

          {/* Question Box */}
          <div className="bg-[#16181D] border border-[#272A30] rounded-xl p-8 flex flex-col gap-6">
            <h3 className="text-[#e3e2e5] text-[16px] leading-relaxed">
              Over the past two weeks, how often have you experienced an irregular or unusually rapid heartbeat while at rest?
            </h3>
            
            <button className="flex items-center gap-2 text-[#8c909f] text-[13px] hover:text-[#e3e2e5] transition-colors w-fit">
              <span className="material-symbols-outlined text-[16px]">info</span>
              Why we're asking this
            </button>

            {/* Options */}
            <div className="flex flex-col gap-3 mt-2">
              {options.map((opt, idx) => (
                <button 
                  key={idx}
                  onClick={() => setSelectedOption(idx)}
                  className={`w-full text-left p-4 rounded-lg border flex justify-between items-center transition-colors ${
                    selectedOption === idx 
                      ? 'border-[#4d8eff] bg-[#4d8eff]/10 text-[#e3e2e5]' 
                      : 'border-[#272A30] bg-transparent text-[#e3e2e5] hover:bg-[#272A30]'
                  }`}
                >
                  <span className="text-[15px]">{opt}</span>
                  {selectedOption === idx && (
                    <span className="material-symbols-outlined text-[#4d8eff]">check_circle</span>
                  )}
                </button>
              ))}
            </div>

            <div className="w-full h-px bg-[#272A30] my-2"></div>

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center">
              <button className="flex items-center gap-2 text-[#e3e2e5] text-[14px] hover:text-white transition-colors py-2 px-4 rounded hover:bg-[#272A30]">
                <span className="material-symbols-outlined text-[18px]">arrow_back</span>
                Previous
              </button>
              <button className="flex items-center gap-2 bg-[#4d8eff] hover:bg-[#3b82f6] text-white px-6 py-2.5 rounded-md text-[14px] font-medium transition-colors">
                Next Question
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Right Context Panel */}
      <aside className="w-[320px] h-full bg-[#121212] flex-shrink-0 flex flex-col overflow-y-auto">
        <div className="h-[60px] flex items-center gap-2 px-6 border-b border-[#272A30] text-[12px] font-mono text-[#8c909f] tracking-wide uppercase shrink-0">
          <span className="material-symbols-outlined text-[16px]">subject</span>
          ASSESSMENT CONTEXT
        </div>

        <div className="p-6 flex flex-col gap-8">
          {/* Patient Info */}
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-[#1C1F26] border border-[#272A30] flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[20px] text-[#8c909f]">face</span>
            </div>
            <div>
              <div className="text-[14px] font-semibold text-[#e3e2e5] font-mono">ID: PT-8824-X</div>
              <div className="text-[13px] text-[#8c909f] font-mono mt-0.5">Female, 42y</div>
            </div>
          </div>

          {/* Adaptation Engine */}
          <div className="bg-[#1C1F26] border border-[#272A30] rounded-xl p-4">
            <div className="flex justify-between items-center mb-3">
              <div className="text-[12px] font-mono text-[#8c909f]">Adaptation Engine</div>
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#00311f] border border-[#00a572] text-[10px] font-mono text-[#4edea3]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#4edea3]"></span>
                Active
              </div>
            </div>
            <p className="text-[13px] text-[#e3e2e5] leading-relaxed">
              Question trajectory modified based on previous answer regarding "Shortness of breath on exertion". Path branching towards cardiopulmonary evaluation.
            </p>
          </div>

          {/* Extracted EHR Data */}
          <div>
            <h3 className="text-[11px] font-mono text-[#8c909f] uppercase tracking-wide mb-4">EXTRACTED EHR DATA</h3>
            <div className="space-y-4">
              <div className="border-l-2 border-[#272A30] pl-3">
                <div className="text-[12px] font-mono text-[#8c909f] mb-1">Last Visit (3mo ago)</div>
                <div className="text-[13px] text-[#e3e2e5]">Patient reported occasional 'fluttering' in chest during stressful events.</div>
              </div>
              <div className="border-l-2 border-[#272A30] pl-3">
                <div className="text-[12px] font-mono text-[#8c909f] mb-1">Current Meds</div>
                <div className="text-[13px] text-[#e3e2e5]">Levothyroxine 50mcg (Note: check TSH levels)</div>
              </div>
            </div>
          </div>

        </div>
      </aside>
    </div>
  );
};

export default Intake;
