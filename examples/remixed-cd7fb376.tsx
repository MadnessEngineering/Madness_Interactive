import React, { useState, useEffect } from 'react';
import { Zap, Wrench, Cog, Rocket, Brain, Flame, Star, Target, Cpu } from 'lucide-react';

const IronHeartTransformer = () => {
  const [projectType, setProjectType] = useState('invention');
  const [context, setContext] = useState({
    invention: {
      concept: '',
      creator: '',
      category: '',
      constraints: ''
    },
    experiment: {
      hypothesis: '',
      researcher: '',
      field: '',
      resources: ''
    }
  });
  const [rawIdeas, setRawIdeas] = useState('');
  const [amplificationMode, setAmplificationMode] = useState('');
  const [output, setOutput] = useState('');
  const [isAmplifying, setIsAmplifying] = useState(false);
  const [sparkles, setSparkles] = useState([]);

  // Animated background sparkles
  useEffect(() => {
    const interval = setInterval(() => {
      setSparkles(prev => [
        ...prev.slice(-20),
        {
          id: Date.now(),
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * 4 + 2,
          duration: Math.random() * 3000 + 2000
        }
      ]);
    }, 300);
    return () => clearInterval(interval);
  }, []);

  const sampleData = {
    invention: {
      context: {
        concept: 'Self-Repairing Neural Mesh',
        creator: 'Tony Stark Jr.',
        category: 'Biotech Enhancement',
        constraints: 'Must be non-invasive, budget unlimited'
      },
      ideas: `Basic idea: neural interface mesh
- thin film conductors
- wireless power transfer
- basic repair protocols
- connects to brain stem
- monitors vital signs
- some AI processing
- might work with existing tech
- could be useful for paralysis
- needs more research
- safety concerns exist`
    },
    experiment: {
      context: {
        hypothesis: 'Quantum Entangled Memory Storage',
        researcher: 'Dr. Reed Richards',
        field: 'Quantum Computing',
        resources: 'Particle accelerator, quantum lab'
      },
      ideas: `Theory: entangled particles for data storage
- photon pairs store bits
- instant access across distance
- might be stable
- could revolutionize computing
- needs quantum isolation
- error correction important
- scalability questions
- cost might be high
- proof of concept first
- measure decoherence rates`
    }
  };

  const amplificationModes = {
    invention: [
      { value: 'breakthrough', label: 'BREAKTHROUGH PROTOCOL', icon: Zap, color: 'from-yellow-400 to-orange-500' },
      { value: 'ironheart', label: 'IRONHEART MANIFEST', icon: Flame, color: 'from-red-500 to-pink-600' },
      { value: 'quantum', label: 'QUANTUM LEAP MODE', icon: Star, color: 'from-purple-500 to-blue-600' }
    ],
    experiment: [
      { value: 'limitless', label: 'LIMITLESS HYPOTHESIS', icon: Brain, color: 'from-cyan-400 to-blue-500' },
      { value: 'paradigm', label: 'PARADIGM SHATTER', icon: Target, color: 'from-green-400 to-emerald-600' },
      { value: 'transcendent', label: 'TRANSCENDENT THEORY', icon: Cpu, color: 'from-indigo-500 to-purple-600' }
    ]
  };

  const contextFields = {
    invention: [
      { key: 'concept', label: 'Core Concept', icon: Brain },
      { key: 'creator', label: 'Mad Inventor', icon: Wrench },
      { key: 'category', label: 'Innovation Field', icon: Cog },
      { key: 'constraints', label: 'Current Limits', icon: Target }
    ],
    experiment: [
      { key: 'hypothesis', label: 'Wild Hypothesis', icon: Zap },
      { key: 'researcher', label: 'Visionary', icon: Wrench },
      { key: 'field', label: 'Science Domain', icon: Cog },
      { key: 'resources', label: 'Available Arsenal', icon: Rocket }
    ]
  };

  const loadSampleData = () => {
    const sample = sampleData[projectType];
    setContext(prev => ({ ...prev, [projectType]: sample.context }));
    setRawIdeas(sample.ideas);
    setAmplificationMode(amplificationModes[projectType][0].value);
  };

  const handleContextChange = (field, value) => {
    setContext(prev => ({
      ...prev,
      [projectType]: {
        ...prev[projectType],
        [field]: value
      }
    }));
  };

  const getAmplificationPrompt = () => {
    const currentContext = context[projectType];
    const contextString = Object.entries(currentContext)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ');

    const modeInstructions = {
      breakthrough: `Transform this into a BREAKTHROUGH INNOVATION that pushes beyond all current limitations. Think Tony Stark meeting Nikola Tesla. Amplify every aspect to maximum potential.`,
      ironheart: `Channel the IRONHEART spirit - Ferrum Corde! Create something that doesn't just solve problems but revolutionizes entire fields. Make it legendary.`,
      quantum: `Apply QUANTUM LEAP thinking - imagine this concept with unlimited resources, perfect materials, and breakthrough physics. What becomes possible?`,
      limitless: `Remove ALL constraints and limitations. What would this experiment become with infinite resources and perfect conditions?`,
      paradigm: `SHATTER the current paradigm. How does this experiment completely rewrite the rules of its field?`,
      transcendent: `Elevate this to TRANSCENDENT levels - beyond current scientific understanding into the realm of controlled impossibility.`
    };

    return `🔥 FERRUM CORDE - IRONHEART AMPLIFICATION PROTOCOL 🔥

${modeInstructions[amplificationMode]}

Context: ${contextString}

Raw Ideas to Amplify:
${rawIdeas}

AMPLIFICATION DIRECTIVE:
- Reject "good enough" - aim for REVOLUTIONARY
- Push beyond all known limitations
- Integrate cutting-edge theoretical possibilities  
- Add brilliant engineering solutions
- Make it worthy of the IronHeart legacy
- Transform basic concepts into world-changing innovations
- Think 10x, then think 10x again
- Channel pure inventive genius

Output should be a detailed, ambitious, technically sophisticated vision that makes the original look like a rough sketch. Make Tony Stark proud! ⚡

FERRUM CORDE! 🚀`;
  };

  const amplifyIdeas = async () => {
    if (!rawIdeas.trim()) return;
    
    setIsAmplifying(true);
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 3000,
          messages: [
            { role: "user", content: getAmplificationPrompt() }
          ]
        })
      });

      if (!response.ok) {
        throw new Error(`Amplification matrix failed: ${response.status}`);
      }

      const data = await response.json();
      setOutput(data.content[0].text);
    } catch (error) {
      console.error("Amplification error:", error);
      setOutput("⚠️ AMPLIFICATION MATRIX OVERLOAD ⚠️\nRecalibrating systems... Please try again, inventor!");
    } finally {
      setIsAmplifying(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(output);
    } catch (err) {
      console.error('Transfer failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-6 relative overflow-hidden">
      {/* Animated background sparkles */}
      {sparkles.map(sparkle => (
        <div
          key={sparkle.id}
          className="absolute rounded-full bg-yellow-400 opacity-70 animate-pulse pointer-events-none"
          style={{
            left: `${sparkle.x}%`,
            top: `${sparkle.y}%`,
            width: `${sparkle.size}px`,
            height: `${sparkle.size}px`,
            animationDuration: `${sparkle.duration}ms`
          }}
        />
      ))}

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Flame className="h-12 w-12 text-orange-500 animate-pulse mr-4" />
            <h1 className="text-5xl font-black bg-gradient-to-r from-orange-400 via-red-500 to-pink-600 bg-clip-text text-transparent">
              IRONHEART AMPLIFIER
            </h1>
            <Lightning className="h-12 w-12 text-yellow-400 animate-pulse ml-4" />
          </div>
          <p className="text-2xl font-bold text-cyan-300 mb-2">FERRUM CORDE!</p>
          <p className="text-gray-300 text-lg">Transform good ideas into LEGENDARY innovations • Push beyond all limits • Be the best like no one ever was!</p>
        </div>

        {/* Project Type Selector */}
        <div className="mb-8 flex justify-center">
          <div className="bg-black/50 backdrop-blur-sm p-2 rounded-2xl border border-cyan-500/30">
            <button
              onClick={() => setProjectType('invention')}
              className={`px-8 py-3 rounded-xl font-bold text-lg transition-all duration-300 ${
                projectType === 'invention'
                  ? 'bg-gradient-to-r from-orange-500 to-red-600 text-white shadow-lg shadow-orange-500/50'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              🔧 MAD INVENTIONS
            </button>
            <button
              onClick={() => setProjectType('experiment')}
              className={`px-8 py-3 rounded-xl font-bold text-lg transition-all duration-300 ${
                projectType === 'experiment'
                  ? 'bg-gradient-to-r from-purple-500 to-blue-600 text-white shadow-lg shadow-purple-500/50'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              ⚗️ WILD EXPERIMENTS
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Column */}
          <div className="space-y-6">
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-cyan-500/30 p-8 shadow-2xl">
              <div className="flex items-center mb-6">
                <Rocket className="h-8 w-8 text-orange-500 mr-3" />
                <h2 className="text-2xl font-bold text-white">INPUT MATRIX</h2>
              </div>
              
              {/* Context Fields */}
              <div className="space-y-6 mb-8">
                <h3 className="text-xl font-bold text-cyan-300 flex items-center">
                  <Brain className="h-6 w-6 mr-2" />
                  PROJECT PARAMETERS
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {contextFields[projectType].map(field => {
                    const Icon = field.icon;
                    return (
                      <div key={field.key} className="relative">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <Icon className="h-5 w-5 text-cyan-400" />
                        </div>
                        <input
                          type="text"
                          placeholder={field.label}
                          value={context[projectType][field.key]}
                          onChange={(e) => handleContextChange(field.key, e.target.value)}
                          className="w-full pl-12 pr-4 py-3 bg-gray-800/50 border border-cyan-500/30 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm"
                        />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Raw Ideas Input */}
              <div className="space-y-4 mb-8">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold text-cyan-300 flex items-center">
                    <Lightning className="h-6 w-6 mr-2" />
                    RAW GENIUS INPUT
                  </h3>
                  <button
                    onClick={loadSampleData}
                    className="bg-gradient-to-r from-yellow-500 to-orange-600 text-black font-bold px-4 py-2 rounded-lg hover:from-yellow-400 hover:to-orange-500 transition-all duration-300"
                  >
                    🔥 LOAD SAMPLE
                  </button>
                </div>
                <textarea
                  value={rawIdeas}
                  onChange={(e) => setRawIdeas(e.target.value)}
                  placeholder="Dump your raw ideas here... even the wildest sketches become legendary inventions! ⚡"
                  rows={12}
                  className="w-full p-6 bg-gray-800/50 border border-cyan-500/30 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyan-400 focus:border-transparent resize-none backdrop-blur-sm"
                />
              </div>

              {/* Amplification Mode Selector */}
              <div className="space-y-4 mb-8">
                <h3 className="text-xl font-bold text-cyan-300 flex items-center">
                  <Zap className="h-6 w-6 mr-2" />
                  AMPLIFICATION PROTOCOL
                </h3>
                <div className="grid grid-cols-1 gap-3">
                  {amplificationModes[projectType].map(mode => {
                    const Icon = mode.icon;
                    return (
                      <button
                        key={mode.value}
                        onClick={() => setAmplificationMode(mode.value)}
                        className={`flex items-center space-x-3 p-4 rounded-xl font-bold transition-all duration-300 ${
                          amplificationMode === mode.value
                            ? `bg-gradient-to-r ${mode.color} text-white shadow-lg transform scale-105`
                            : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50 border border-gray-600/30'
                        }`}
                      >
                        <Icon className="h-6 w-6" />
                        <span>{mode.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Amplify Button */}
              <button
                onClick={amplifyIdeas}
                disabled={!rawIdeas.trim() || isAmplifying}
                className="w-full bg-gradient-to-r from-red-600 via-orange-500 to-yellow-500 text-black font-black text-xl py-4 px-8 rounded-xl hover:from-red-500 hover:via-orange-400 hover:to-yellow-400 disabled:from-gray-600 disabled:to-gray-700 disabled:text-gray-400 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-2xl"
              >
                {isAmplifying ? (
                  <div className="flex items-center justify-center">
                    <Cog className="h-6 w-6 animate-spin mr-3" />
                    AMPLIFYING GENIUS...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Flame className="h-6 w-6 mr-3" />
                    🚀 AMPLIFY TO LEGENDARY STATUS! ⚡
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Output Column */}
          <div className="space-y-6">
            <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-cyan-500/30 p-8 shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center">
                  <Star className="h-8 w-8 text-yellow-400 mr-3" />
                  <h2 className="text-2xl font-bold text-white">LEGENDARY OUTPUT</h2>
                </div>
                {output && (
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold px-4 py-2 rounded-lg hover:from-cyan-400 hover:to-blue-500 transition-all duration-300"
                  >
                    <Zap className="h-4 w-4" />
                    <span>TRANSFER</span>
                  </button>
                )}
              </div>
              
              <div className="min-h-[500px] p-6 bg-gray-900/50 rounded-xl border border-cyan-500/20 backdrop-blur-sm">
                {output ? (
                  <div className="whitespace-pre-wrap text-gray-100 leading-relaxed text-lg">
                    {output}
                  </div>
                ) : (
                  <div className="text-center py-20">
                    <div className="relative">
                      <Rocket className="h-20 w-20 mx-auto mb-6 text-cyan-400 animate-bounce" />
                      <div className="absolute top-0 left-1/2 transform -translate-x-1/2">
                        <Star className="h-6 w-6 text-yellow-400 animate-pulse" />
                      </div>
                    </div>
                    <p className="text-cyan-300 text-xl font-bold mb-2">AMPLIFICATION MATRIX READY</p>
                    <p className="text-gray-400">Your legendary innovations will manifest here</p>
                    <p className="text-orange-400 font-bold mt-4">FERRUM CORDE! 🔥</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-gray-400 text-lg mb-2">
            "Good enough is the enemy of legendary" - IronHeart Creed
          </p>
          <p className="text-cyan-300 font-bold text-xl">
            ⚡ FERRUM CORDE ⚡
          </p>
        </div>
      </div>
    </div>
  );
};

export default IronHeartTransformer;