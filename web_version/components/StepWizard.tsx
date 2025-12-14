import React from 'react';
import { AppStep } from '../types';

interface StepWizardProps {
  currentStep: AppStep;
}

export const StepWizard: React.FC<StepWizardProps> = ({ currentStep }) => {
  const steps = [
    { id: AppStep.SCENARIO, label: 'Scenario' },
    { id: AppStep.IMAGERY, label: 'Visuals' },
    { id: AppStep.AUDIO, label: 'Audio' },
    { id: AppStep.ASSEMBLY, label: 'Render' },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto mb-10">
      <div className="flex justify-between relative">
        {/* Connecting Line */}
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-800 -z-10 transform -translate-y-1/2"></div>
        
        {steps.map((step, index) => {
            const isActive = currentStep === step.id;
            const isCompleted = currentStep > step.id;
            
            return (
                <div key={step.id} className="flex flex-col items-center gap-2 bg-[#050505] px-2">
                    <div className={`
                        w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300
                        ${isActive ? 'border-blood bg-blood/20 text-white shadow-[0_0_15px_rgba(138,11,11,0.6)] scale-110' : ''}
                        ${isCompleted ? 'border-green-600 bg-green-900/20 text-green-500' : ''}
                        ${!isActive && !isCompleted ? 'border-gray-700 text-gray-500' : ''}
                    `}>
                        {isCompleted ? (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        ) : (
                            <span className="font-mono text-sm">{index + 1}</span>
                        )}
                    </div>
                    <span className={`text-xs font-medium uppercase tracking-wider ${isActive ? 'text-white' : 'text-gray-600'}`}>
                        {step.label}
                    </span>
                </div>
            )
        })}
      </div>
    </div>
  );
};