import React, { useState, useEffect, useRef } from 'react';
import { Download, Type, Palette, Settings, ChevronDown, ChevronUp } from 'lucide-react';

const TRANSLATIONS = {
  "en-US": {
    "pageTitle": "Word cloud generator",
    "pageSubtitle": "Create beautiful visualizations from your text",
    "textInputLabel": "Text input",
    "textInputPlaceholder": "Paste your text here...",
    "trySampleText": "Try sample text:",
    "sampleTechnology": "Technology",
    "sampleBusiness": "Business",
    "sampleNature": "Nature",
    "sampleCreativity": "Creativity",
    "settingsTitle": "Settings",
    "maxWordsLabel": "Max words",
    "minFrequencyLabel": "Min frequency",
    "colorSchemeLabel": "Color scheme",
    "colorSchemeBlues": "Blues",
    "colorSchemeReds": "Reds",
    "colorSchemeGreens": "Greens",
    "colorSchemePurples": "Purples",
    "colorSchemeRainbow": "Rainbow",
    "downloadButton": "Download SVG",
    "wordCloudTitle": "Word cloud",
    "emptyStateMessage": "Paste text to create your word cloud"
  },
  /* LOCALE_PLACEHOLDER_START */
  "es-ES": {
    "pageTitle": "Generador de nube de palabras",
    "pageSubtitle": "Crea hermosas visualizaciones a partir de tu texto",
    "textInputLabel": "Entrada de texto",
    "textInputPlaceholder": "Pega tu texto aquí...",
    "trySampleText": "Prueba texto de muestra:",
    "sampleTechnology": "Tecnología",
    "sampleBusiness": "Negocios",
    "sampleNature": "Naturaleza",
    "sampleCreativity": "Creatividad",
    "settingsTitle": "Configuración",
    "maxWordsLabel": "Máximo de palabras",
    "minFrequencyLabel": "Frecuencia mínima",
    "colorSchemeLabel": "Esquema de colores",
    "colorSchemeBlues": "Azules",
    "colorSchemeReds": "Rojos",
    "colorSchemeGreens": "Verdes",
    "colorSchemePurples": "Púrpuras",
    "colorSchemeRainbow": "Arcoíris",
    "downloadButton": "Descargar SVG",
    "wordCloudTitle": "Nube de palabras",
    "emptyStateMessage": "Pega texto para crear tu nube de palabras"
  }
  /* LOCALE_PLACEHOLDER_END */
};

const appLocale = '{{APP_LOCALE}}';
const browserLocale = navigator.languages?.[0] || navigator.language || 'en-US';
const findMatchingLocale = (locale) => {
  if (TRANSLATIONS[locale]) return locale;
  const lang = locale.split('-')[0];
  const match = Object.keys(TRANSLATIONS).find(key => key.startsWith(lang + '-'));
  return match || 'en-US';
};
const locale = (appLocale !== '{{APP_LOCALE}}') ? findMatchingLocale(appLocale) : findMatchingLocale(browserLocale);
const t = (key) => TRANSLATIONS[locale]?.[key] || TRANSLATIONS['en-US'][key] || key;

const WordCloudGenerator = () => {
  const [text, setText] = useState('');
  const [wordData, setWordData] = useState([]);
  const [maxWords, setMaxWords] = useState(100);
  const [minFrequency, setMinFrequency] = useState(2);
  const [colorScheme, setColorScheme] = useState('blues');
  const [showSettings, setShowSettings] = useState(false);
  const svgRef = useRef(null);
  
  // Sample texts for quick start
  const sampleTexts = {
    [t('sampleTechnology')]: `The digital revolution has transformed every aspect of our lives, from how we communicate to how we work and play. Artificial intelligence and machine learning algorithms now power everything from recommendation systems to autonomous vehicles, while cloud computing infrastructure enables unprecedented scalability for businesses of all sizes. The Internet of Things connects billions of devices worldwide, creating vast networks of data that companies analyze to improve their products and services. Blockchain technology promises to revolutionize financial systems, ensuring transparency and security in digital transactions. As we advance, cybersecurity becomes increasingly critical, with organizations investing heavily in protecting their digital assets from sophisticated threats. Software engineering practices have evolved to embrace agile methodologies, DevOps culture, and continuous integration pipelines that accelerate development cycles. Open source projects foster innovation through global collaboration, while tech startups disrupt traditional industries with innovative solutions. The future of technology looks toward quantum computing, augmented reality, and sustainable digital infrastructure that powers our connected world responsibly.`,
    
    [t('sampleBusiness')]: `In today's competitive business landscape, successful companies must balance innovation with operational excellence to achieve sustainable growth. Leadership teams focus on developing comprehensive strategies that align with their organization's mission and vision while adapting to rapidly changing market conditions. Customer experience has become the ultimate differentiator, with businesses investing heavily in understanding and meeting evolving customer needs. Digital transformation initiatives reshape traditional business models, requiring companies to modernize their technology infrastructure and workflow processes. Effective project management ensures that strategic initiatives are executed efficiently, while data analytics provide insights that drive informed decision-making. Strong company culture attracts top talent and fosters employee engagement, creating teams that deliver exceptional results. Supply chain optimization and logistics management have become critical factors in maintaining competitive advantage, especially in global markets. Marketing and sales strategies now leverage multiple channels, from traditional advertising to social media campaigns and content marketing. Financial performance metrics guide strategic planning, while risk management frameworks protect organizations from potential threats. Stakeholder relationships, including investors, employees, and customers, require careful attention and transparent communication to build lasting trust and loyalty.`,
    
    [t('sampleNature')]: `The natural world encompasses an extraordinary diversity of ecosystems, from dense rainforests teeming with life to vast deserts and deep ocean trenches. Climate change poses unprecedented challenges to biodiversity, threatening countless species with habitat loss and environmental disruption. Conservation efforts worldwide work tirelessly to protect endangered wildlife and preserve critical habitats for future generations. Sustainable development practices aim to balance human progress with environmental stewardship, recognizing that our economic systems depend on healthy ecosystems. Renewable energy technologies, including solar and wind power, offer pathways toward reducing our carbon footprint and mitigating climate impacts. Forest restoration projects help combat deforestation while providing carbon sequestration benefits that address global warming concerns. Ocean conservation initiatives focus on protecting marine life from pollution, overfishing, and habitat destruction. National parks and nature reserves serve as sanctuaries for wildlife and educational resources for the public. Environmental awareness continues to grow as people recognize their connection to nature and responsibility for planetary health. Green technologies and sustainable practices in agriculture, manufacturing, and transportation represent hopeful trends toward a more environmentally conscious future. The interconnectedness of all living systems reminds us that protecting nature ultimately protects humanity itself.`,
    
    [t('sampleCreativity')]: `Creative expression manifests in countless forms, from traditional arts like painting and sculpture to digital media, music production, and innovative design. Artists throughout history have pushed boundaries, challenging conventions and exploring new possibilities for human expression. The creative process often involves periods of inspiration followed by dedicated practice and refinement of skills. Imagination serves as the foundation for innovation, enabling individuals to envision possibilities that don't yet exist. Creative industries, including film, fashion, graphic design, and advertising, contribute significantly to global economies while shaping cultural narratives. Collaboration between artists, designers, and technologists produces groundbreaking works that blend traditional techniques with modern tools. Creative writing encompasses novels, poetry, screenplays, and journalism, each requiring unique storytelling approaches and narrative techniques. Visual arts continue to evolve with new technologies, from digital painting to virtual reality installations that immerse viewers in artistic experiences. Music composition and production have democratized through accessible software, allowing more people to create and share their artistic visions. Design thinking applies creative problem-solving methodologies to business challenges, user experience design, and product development. The intersection of art and science often yields surprising innovations, demonstrating that creativity knows no boundaries between disciplines. Nurturing creative thinking skills benefits individuals and organizations alike, fostering innovation and adaptability in an ever-changing world.`
  };
  
  // Common stop words to filter out
  const stopWords = new Set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he',
    'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or',
    'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about',
    'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
    'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our',
    'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
  ]);

  // Color schemes - professional but vibrant
  const colorSchemes = {
    blues: ['#0B4F6C', '#1E6F96', '#3E92C1', '#66B5E5', '#8DCFF0'],
    reds: ['#9B1C26', '#C92B36', '#E64B57', '#F07383', '#F8A3B0'],
    greens: ['#1B5E20', '#2E7D32', '#43A047', '#66BB6A', '#81C784'],
    purples: ['#4A148C', '#6A1B9A', '#7B1FA2', '#8E24AA', '#9C27B0'],
    rainbow: ['#E91E63', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#F44336']
  };

  // Process text and calculate word frequencies
  const processText = (inputText) => {
    if (!inputText.trim()) {
      setWordData([]);
      return;
    }

    // Clean and split text
    const words = inputText
      .toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 2 && !stopWords.has(word));

    // Count frequencies
    const frequencies = {};
    words.forEach(word => {
      frequencies[word] = (frequencies[word] || 0) + 1;
    });

    // Convert to array and sort
    const sortedWords = Object.entries(frequencies)
      .filter(([, freq]) => freq >= minFrequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, maxWords);

    // Calculate sizes
    const maxFreq = sortedWords[0]?.[1] || 1;
    const minSize = 16;
    const maxSize = 72;

    const processedWords = sortedWords.map(([word, freq]) => ({
      text: word,
      size: minSize + (freq / maxFreq) * (maxSize - minSize),
      frequency: freq,
      color: colorSchemes[colorScheme][Math.floor(Math.random() * colorSchemes[colorScheme].length)]
    }));

    setWordData(processedWords);
  };

  // Layout algorithm - improved spiral layout with viewport fitting
  const generateLayout = () => {
    if (!wordData.length) return [];

    const width = 800;
    const height = 500;
    const cx = width / 2;
    const cy = height / 2;
    const padding = 50; // Add padding from edges
    
    const positions = [];
    
    wordData.forEach((word, i) => {
      let angle = 0;
      let radius = 0;
      let positioned = false;
      let attempts = 0;
      const maxAttempts = 1000;
      
      while (!positioned && attempts < maxAttempts) {
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        
        // More accurate text metrics
        const textWidth = word.text.length * word.size * 0.5;
        const textHeight = word.size * 0.8;
        
        // Check bounds with padding
        if (x - textWidth/2 < padding || x + textWidth/2 > width - padding ||
            y - textHeight/2 < padding || y + textHeight/2 > height - padding) {
          angle += 0.3;
          radius += 0.3;
          attempts++;
          continue;
        }
        
        // Check for collisions
        let collision = false;
        for (const pos of positions) {
          const dx = Math.abs(x - pos.x);
          const dy = Math.abs(y - pos.y);
          const minDist = (textWidth + pos.width) / 2 + 8; // Add spacing
          const minDistY = (textHeight + pos.height) / 2 + 4;
          
          if (dx < minDist && dy < minDistY) {
            collision = true;
            break;
          }
        }
        
        if (!collision) {
          positions.push({
            ...word,
            x: x,
            y: y,
            width: textWidth,
            height: textHeight,
            rotation: Math.random() > 0.8 ? Math.random() * 30 - 15 : 0
          });
          positioned = true;
        } else {
          angle += 0.3;
          radius += 0.3;
        }
        attempts++;
      }
    });
    
    return positions;
  };

  // Update word cloud when text or settings change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      processText(text);
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [text, minFrequency, maxWords, colorScheme]);

  // Generate layout when word data changes
  const layoutData = generateLayout();

  // Download SVG
  const downloadSVG = () => {
    if (!svgRef.current) return;
    
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    
    const downloadLink = document.createElement('a');
    downloadLink.href = svgUrl;
    downloadLink.download = 'wordcloud.svg';
    downloadLink.click();
    
    URL.revokeObjectURL(svgUrl);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-medium text-gray-800 mb-1">{t('pageTitle')}</h1>
          <p className="text-gray-500 text-sm">{t('pageSubtitle')}</p>
        </div>
        
        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-600 mb-2">{t('textInputLabel')}</label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={t('textInputPlaceholder')}
                  className="w-full h-32 px-3 py-2 border border-gray-200 rounded-md text-sm resize-none focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <div className="mt-2">
                  <p className="text-xs text-gray-400 mb-1">{t('trySampleText')}</p>
                  <div className="flex flex-wrap gap-1">
                    {Object.keys(sampleTexts).map((category) => (
                      <button
                        key={category}
                        onClick={() => setText(sampleTexts[category])}
                        className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-md transition-colors"
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="flex items-center justify-between w-full text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Settings size={16} />
                    <span>{t('settingsTitle')}</span>
                  </div>
                  {showSettings ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
                
                {showSettings && (
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">{t('maxWordsLabel')}: {maxWords}</label>
                      <input
                        type="range"
                        min="20"
                        max="200"
                        value={maxWords}
                        onChange={(e) => setMaxWords(Number(e.target.value))}
                        className="w-full accent-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">{t('minFrequencyLabel')}: {minFrequency}</label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={minFrequency}
                        onChange={(e) => setMinFrequency(Number(e.target.value))}
                        className="w-full accent-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">{t('colorSchemeLabel')}</label>
                      <select
                        value={colorScheme}
                        onChange={(e) => setColorScheme(e.target.value)}
                        className="w-full p-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="blues">{t('colorSchemeBlues')}</option>
                        <option value="reds">{t('colorSchemeReds')}</option>
                        <option value="greens">{t('colorSchemeGreens')}</option>
                        <option value="purples">{t('colorSchemePurples')}</option>
                        <option value="rainbow">{t('colorSchemeRainbow')}</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
              
              <button
                onClick={downloadSVG}
                disabled={!wordData.length}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                <Download size={16} />
                {t('downloadButton')}
              </button>
            </div>
          </div>
          
          {/* Word Cloud Display */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-sm font-medium text-gray-600 mb-4">{t('wordCloudTitle')}</h2>
              
              <div className="border border-gray-100 rounded-lg overflow-hidden bg-gray-50">
                <svg 
                  ref={svgRef} 
                  width="800" 
                  height="500" 
                  className="w-full bg-white" 
                  viewBox="0 0 800 500"
                >
                  <rect width="800" height="500" fill="white" />
                  {layoutData.map((word, i) => (
                    <g key={i}>
                      <text
                        x={word.x}
                        y={word.y}
                        fontSize={word.size}
                        fill={word.color}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        transform={`rotate(${word.rotation}, ${word.x}, ${word.y})`}
                        fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
                        fontWeight="600"
                      >
                        {word.text}
                      </text>
                    </g>
                  ))}
                </svg>
              </div>
              
              {wordData.length === 0 && (
                <div className="text-center text-gray-400 mt-8 py-12">
                  <Type size={32} className="mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">{t('emptyStateMessage')}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WordCloudGenerator;