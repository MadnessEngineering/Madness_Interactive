import React, { useState, useEffect, useRef } from 'react';

const TRANSLATIONS = {
  "en-US": {
    "stepOutsideTitle": "Time to step outside",
    "nightGrassSecrets": "The night grass holds its secrets...",
    "dawnBreaksSecrets": "Dawn breaks, revealing hidden treasures...",
    "eveningSettlesSecrets": "Evening settles, bringing new mysteries...",
    "twilightTransforms": "Twilight transforms the grass...",
    "magicWaitingGrass": "There's magic waiting in the grass...",
    "whereExploreInput": "where will you explore?",
    "shuffleLocationTitle": "Shuffle location",
    "goTouchGrassButton": "Go touch some grass",
    "timeOutsideLabel": "Time outside",
    "timeOfDayLabel": "Time of day",
    "locationLabel": "Location",
    "discoveriesLabel": "Discoveries",
    "goBackInsideButton": "Go back inside",
    "grassAdventureTitle": "Your grass adventure",
    "locationGrassAdventureTitle": "Your {location} grass adventure",
    "yourDiscoveriesTitle": "Your discoveries",
    "professionalGrassAvoider": "Achievement unlocked: \nProfessional grass avoider",
    "rareFinds": "RARE FINDS",
    "uncommonFinds": "UNCOMMON FINDS",
    "commonFinds": "COMMON FINDS",
    "goOutsideAgainButton": "Go outside again",
    "youFoundText": "You found {item}",
    "tinyTreasure": "a tiny treasure",
    "smallWonder": "a small wonder",
    "somethingSpecial": "something special",
    "curiousFind": "a curious find",
    "hiddenGem": "a hidden gem",
    "dawnTimeOfDay": "Dawn",
    "morningTimeOfDay": "Morning",
    "dayTimeOfDay": "Day",
    "duskTimeOfDay": "Dusk",
    "eveningTimeOfDay": "Evening",
    "nightTimeOfDay": "Night"
  },
  /* LOCALE_PLACEHOLDER_START */
  "es-ES": {
    "stepOutsideTitle": "Hora de salir afuera",
    "nightGrassSecrets": "La hierba nocturna guarda sus secretos...",
    "dawnBreaksSecrets": "El amanecer revela tesoros ocultos...",
    "eveningSettlesSecrets": "La tarde se asienta, trayendo nuevos misterios...",
    "twilightTransforms": "El crepúsculo transforma la hierba...",
    "magicWaitingGrass": "Hay magia esperando en la hierba...",
    "whereExploreInput": "¿dónde vas a explorar?",
    "shuffleLocationTitle": "Cambiar ubicación",
    "goTouchGrassButton": "Ve a tocar hierba",
    "timeOutsideLabel": "Tiempo afuera",
    "timeOfDayLabel": "Hora del día",
    "locationLabel": "Ubicación",
    "discoveriesLabel": "Descubrimientos",
    "goBackInsideButton": "Volver adentro",
    "grassAdventureTitle": "Tu aventura en la hierba",
    "locationGrassAdventureTitle": "Tu aventura en la hierba de {location}",
    "yourDiscoveriesTitle": "Tus descubrimientos",
    "professionalGrassAvoider": "Logro desbloqueado: \nEvitador profesional de hierba",
    "rareFinds": "HALLAZGOS RAROS",
    "uncommonFinds": "HALLAZGOS POCO COMUNES",
    "commonFinds": "HALLAZGOS COMUNES",
    "goOutsideAgainButton": "Salir afuera otra vez",
    "youFoundText": "Encontraste {item}",
    "tinyTreasure": "un pequeño tesoro",
    "smallWonder": "una pequeña maravilla",
    "somethingSpecial": "algo especial",
    "curiousFind": "un hallazgo curioso",
    "hiddenGem": "una gema oculta",
    "dawnTimeOfDay": "Amanecer",
    "morningTimeOfDay": "Mañana",
    "dayTimeOfDay": "Día",
    "duskTimeOfDay": "Atardecer",
    "eveningTimeOfDay": "Tarde",
    "nightTimeOfDay": "Noche"
  }
  /* LOCALE_PLACEHOLDER_END */
};

const appLocale = '{{APP_LOCALE}}';
const browserLocale = navigator.languages && navigator.languages[0] || navigator.language || 'en-US';
const findMatchingLocale = (locale) => {
  if (TRANSLATIONS[locale]) return locale;
  const lang = locale.split('-')[0];
  const match = Object.keys(TRANSLATIONS).find(key => key.startsWith(lang + '-'));
  return match || 'en-US';
};
const locale = (appLocale !== '{{APP_LOCALE}}') ? findMatchingLocale(appLocale) : findMatchingLocale(browserLocale);
const t = (key) => (TRANSLATIONS[locale] && TRANSLATIONS[locale][key]) || TRANSLATIONS['en-US'][key] || key;

const TouchGrassGame = () => {
  const canvasRef = useRef(null);
  const starsRef = useRef(null);
  const [grass, setGrass] = useState([]);
  const [screenSize, setScreenSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [floatingDiscoveries, setFloatingDiscoveries] = useState([]);
  const [hiddenSpots, setHiddenSpots] = useState([]);
  const [currentTime, setCurrentTime] = useState('day');
  const [hour, setHour] = useState(new Date().getHours());
  const [isCreatingDiscovery, setIsCreatingDiscovery] = useState(false);
  const [secondsOutside, setSecondsOutside] = useState(0);
  const [foundItems, setFoundItems] = useState([]);
  const [phase, setPhase] = useState('welcome'); // 'welcome', 'exploring', 'results'
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const [explorePlaceName, setExplorePlaceName] = useState('');
  const [itemHistory, setItemHistory] = useState({});
  const [lastFoundItems, setLastFoundItems] = useState([]);
  const [soundContext, setSoundContext] = useState(null);
  const [ambientVolume, setAmbientVolume] = useState(null);
  
  // Setup audio system
  useEffect(() => {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    setSoundContext(audioCtx);
    
    // Create ambient sound system
    const mainGain = audioCtx.createGain();
    mainGain.gain.value = 0;
    
    // Wind noise generator
    const bufferLength = 2 * audioCtx.sampleRate;
    const windBuffer = audioCtx.createBuffer(1, bufferLength, audioCtx.sampleRate);
    const windData = windBuffer.getChannelData(0);
    
    for (let i = 0; i < bufferLength; i++) {
      windData[i] = Math.random() * 2 - 1;
    }
    
    const windSource = audioCtx.createBufferSource();
    windSource.buffer = windBuffer;
    windSource.loop = true;
    
    const windLowpass = audioCtx.createBiquadFilter();
    windLowpass.type = 'lowpass';
    windLowpass.frequency.value = 500;
    
    const windGain = audioCtx.createGain();
    windGain.gain.value = 0.3;
    
    windSource.connect(windLowpass);
    windLowpass.connect(windGain);
    windGain.connect(mainGain);
    windSource.start(0);
    
    // Bird sound generator
    const makeBirdSound = () => {
      const birdOsc = audioCtx.createOscillator();
      const birdGain = audioCtx.createGain();
      const birdFilter = audioCtx.createBiquadFilter();
      
      birdOsc.type = 'sine';
      birdFilter.type = 'bandpass';
      birdFilter.frequency.value = 2500;
      birdFilter.Q.value = 10;
      
      const frequency = 2000 + Math.random() * 1000;
      const startTime = audioCtx.currentTime + Math.random() * 5;
      
      birdOsc.frequency.setValueAtTime(frequency, startTime);
      birdOsc.frequency.linearRampToValueAtTime(frequency + 500, startTime + 0.05);
      birdOsc.frequency.linearRampToValueAtTime(frequency, startTime + 0.1);
      
      birdGain.gain.setValueAtTime(0, startTime);
      birdGain.gain.linearRampToValueAtTime(0.06, startTime + 0.01);
      birdGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.1);
      
      birdOsc.connect(birdFilter);
      birdFilter.connect(birdGain);
      birdGain.connect(mainGain);
      
      birdOsc.start(startTime);
      birdOsc.stop(startTime + 0.1);
    };
    
    // Schedule bird sounds based on time
    const birdTimer = setInterval(() => {
      const currentHour = new Date().getHours();
      let birdProbability = 0.3;
      
      if (currentHour >= 5 && currentHour < 9) {
        birdProbability = 0.7;
      } else if (currentHour >= 9 && currentHour < 17) {
        birdProbability = 0.4;
      } else if (currentHour >= 17 && currentHour < 19) {
        birdProbability = 0.3;
      } else {
        birdProbability = 0.05;
      }
      
      if (Math.random() < birdProbability) {
        makeBirdSound();
      }
    }, 2000);
    
    // Cricket sound generator
    const makeCricketSound = () => {
      const cricketOsc = audioCtx.createOscillator();
      const cricketGain = audioCtx.createGain();
      
      cricketOsc.type = 'square';
      cricketOsc.frequency.value = 4000;
      
      const startTime = audioCtx.currentTime;
      for (let i = 0; i < 8; i++) {
        cricketGain.gain.setValueAtTime(0, startTime + i * 0.1);
        cricketGain.gain.linearRampToValueAtTime(0.02, startTime + i * 0.1 + 0.01);
        cricketGain.gain.linearRampToValueAtTime(0, startTime + i * 0.1 + 0.05);
      }
      
      cricketOsc.connect(cricketGain);
      cricketGain.connect(mainGain);
      
      cricketOsc.start(startTime);
      cricketOsc.stop(startTime + 1);
    };
    
    // Schedule cricket sounds
    const cricketTimer = setInterval(() => {
      const currentHour = new Date().getHours();
      let cricketProbability = 0.2;
      
      if (currentHour >= 19 || currentHour < 5) {
        cricketProbability = 0.7;
      } else if (currentHour >= 17 && currentHour < 19) {
        cricketProbability = 0.4;
      } else if (currentHour >= 5 && currentHour < 7) {
        cricketProbability = 0.2;
      } else {
        cricketProbability = 0.05;
      }
      
      if (Math.random() < cricketProbability) {
        makeCricketSound();
      }
    }, 3000);
    
    mainGain.connect(audioCtx.destination);
    setAmbientVolume(mainGain);
    
    return () => {
      windSource.stop();
      clearInterval(birdTimer);
      clearInterval(cricketTimer);
      audioCtx.close();
    };
  }, []);
  
  // Create discovery sound
  const playFoundSound = (rarity) => {
    if (!soundContext) return;
    
    if (rarity < 0.7) {
      // Common find - gentle chime
      const osc = soundContext.createOscillator();
      const gain = soundContext.createGain();
      
      osc.type = 'sine';
      osc.frequency.value = 1500;
      
      gain.gain.setValueAtTime(0, soundContext.currentTime);
      gain.gain.linearRampToValueAtTime(0.05, soundContext.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, soundContext.currentTime + 0.15);
      
      osc.connect(gain);
      gain.connect(soundContext.destination);
      
      osc.start();
      osc.stop(soundContext.currentTime + 0.15);
      
    } else if (rarity < 0.9) {
      // Uncommon find - sparkly sound
      for (let i = 0; i < 2; i++) {
        const osc = soundContext.createOscillator();
        const gain = soundContext.createGain();
        
        osc.type = 'sine';
        osc.frequency.value = 2000 + (i * 500);
        
        const startTime = soundContext.currentTime + (i * 0.05);
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(0.04, startTime + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.2);
        
        osc.connect(gain);
        gain.connect(soundContext.destination);
        
        osc.start(startTime);
        osc.stop(startTime + 0.2);
      }
      
    } else {
      // Rare find - magical shimmer
      const osc1 = soundContext.createOscillator();
      const osc2 = soundContext.createOscillator();
      const gain1 = soundContext.createGain();
      const gain2 = soundContext.createGain();
      
      osc1.type = 'sine';
      osc2.type = 'sine';
      osc1.frequency.value = 800;
      osc2.frequency.value = 1200;
      
      const filter = soundContext.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 4000;
      filter.Q.value = 0.5;
      
      [gain1, gain2].forEach(gain => {
        gain.gain.setValueAtTime(0, soundContext.currentTime);
        gain.gain.linearRampToValueAtTime(0.03, soundContext.currentTime + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, soundContext.currentTime + 0.8);
      });
      
      osc1.connect(gain1);
      osc2.connect(gain2);
      gain1.connect(filter);
      gain2.connect(filter);
      filter.connect(soundContext.destination);
      
      osc1.start();
      osc2.start();
      
      osc1.stop(soundContext.currentTime + 0.8);
      osc2.stop(soundContext.currentTime + 0.8);
    }
  };
  
  // Control ambient sound volume
  useEffect(() => {
    if (ambientVolume && soundContext) {
      if (phase === 'exploring') {
        let targetVolume = 0.1;
        if (currentTime === 'night' || currentTime === 'evening') {
          targetVolume = 0.15;
        } else if (currentTime === 'dawn' || currentTime === 'dusk') {
          targetVolume = 0.12;
        }
        ambientVolume.gain.linearRampToValueAtTime(targetVolume, soundContext.currentTime + 1);
      } else {
        ambientVolume.gain.linearRampToValueAtTime(0, soundContext.currentTime + 1);
      }
    }
  }, [phase, ambientVolume, soundContext, currentTime]);
  
  // Location options for random selection
  const placeOptions = [
    'backyard',
    'soccer field', 
    'golf course',
    'school playground',
    'picnic area',
    'meadow',
    'city park',
    'rooftop garden',
    'abandoned lot',
    'zen garden',
    'dog park',
    'highway rest stop',
    'church grounds',
    'college quad',
    'botanical garden',
    'festival grounds',
    'mini-golf course',
    'baseball diamond',
    'cemetery',
    'neighbor\'s perfect lawn',
    'Singapore botanical gardens',
    'New York Central Park',
    'Tokyo Imperial Gardens',
    'London Hyde Park',
    'Sydney Royal Botanic Garden',
    'Paris Luxembourg Gardens',
    'Barcelona Park Güell',
    'Vancouver Stanley Park',
    'Beijing Temple of Heaven Park',
    'Dubai Zabeel Park'
  ];
  
  // Random location picker
  const pickRandomPlace = () => {
    const currentIndex = placeOptions.indexOf(explorePlaceName);
    let newIndex;
    
    do {
      newIndex = Math.floor(Math.random() * placeOptions.length);
    } while (newIndex === currentIndex && placeOptions.length > 1);
    
    setExplorePlaceName(placeOptions[newIndex]);
  };
  
  // Load custom font
  useEffect(() => {
    const fontLink = document.createElement('link');
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600&display=swap';
    fontLink.rel = 'stylesheet';
    document.head.appendChild(fontLink);
    
    return () => {
      document.head.removeChild(fontLink);
    };
  }, []);
  
  // Update time of day
  useEffect(() => {
    const checkTimeOfDay = () => {
      const currentHour = new Date().getHours();
      setHour(currentHour);
      
      if (currentHour >= 5 && currentHour < 7) {
        setCurrentTime('dawn');
      } else if (currentHour >= 7 && currentHour < 10) {
        setCurrentTime('morning');
      } else if (currentHour >= 10 && currentHour < 17) {
        setCurrentTime('day');
      } else if (currentHour >= 17 && currentHour < 19) {
        setCurrentTime('dusk');
      } else if (currentHour >= 19 && currentHour < 21) {
        setCurrentTime('evening');
      } else {
        setCurrentTime('night');
      }
    };
    
    checkTimeOfDay();
    const timeInterval = setInterval(checkTimeOfDay, 60000);
    
    return () => clearInterval(timeInterval);
  }, []);
  
  // Timer management
  useEffect(() => {
    let timerInterval;
    if (isTimerRunning) {
      const startTimestamp = Date.now() - secondsOutside * 1000;
      timerInterval = setInterval(() => {
        setSecondsOutside(Math.floor((Date.now() - startTimestamp) / 1000));
      }, 1000);
    }
    return () => clearInterval(timerInterval);
  }, [isTimerRunning]);
  
  // Format timer display
  const formatTimer = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  
  // Generate grass colors based on time
  const getGrassColor = (timeOfDay) => {
    let hue, saturation, lightness;
    
    switch (timeOfDay) {
      case 'dawn':
        hue = 95 + Math.random() * 20;
        saturation = 50 + Math.random() * 20;
        lightness = 30 + Math.random() * 15;
        break;
      case 'morning':
        hue = 100 + Math.random() * 30;
        saturation = 60 + Math.random() * 20;
        lightness = 25 + Math.random() * 20;
        break;
      case 'day':
        hue = 100 + Math.random() * 30;
        saturation = 70 + Math.random() * 20;
        lightness = 25 + Math.random() * 20;
        break;
      case 'dusk':
        hue = 85 + Math.random() * 20;
        saturation = 40 + Math.random() * 20;
        lightness = 20 + Math.random() * 15;
        break;
      case 'evening':
        hue = 90 + Math.random() * 20;
        saturation = 30 + Math.random() * 20;
        lightness = 15 + Math.random() * 10;
        break;
      case 'night':
        hue = 100 + Math.random() * 20;
        saturation = 20 + Math.random() * 10;
        lightness = 10 + Math.random() * 10;
        break;
      default:
        hue = 100 + Math.random() * 30;
        saturation = 70;
        lightness = 25 + Math.random() * 20;
    }
    
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };
  
  // Handle screen resize
  useEffect(() => {
    const handleResize = () => {
      setScreenSize({ width: window.innerWidth, height: window.innerHeight });
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Create discoverable spots
  useEffect(() => {
    const spots = [];
    for (let i = 0; i < 5; i++) {
      const margin = 100;
      spots.push({
        x: margin + Math.random() * (screenSize.width - 2 * margin),
        y: screenSize.height - 10 - Math.random() * 150,
        found: false,
        rarity: Math.random()
      });
    }
    setHiddenSpots(spots);
  }, [screenSize]);

  // Generate grass field
  useEffect(() => {
    const grassCount = Math.floor((screenSize.width * screenSize.height) / 500);
    const grassBlades = [];
    
    for (let i = 0; i < grassCount; i++) {
      grassBlades.push({
        x: Math.random() * screenSize.width,
        baseY: screenSize.height - 10 - Math.random() * 200,
        height: 40 + Math.random() * 60,
        angle: 0,
        targetAngle: 0,
        width: 2 + Math.random() * 3,
        sway: Math.random() * Math.PI * 2,
        swaySpeed: 0.02 + Math.random() * 0.03,
        swayIntensity: 0.01 + Math.random() * 0.03,
        springiness: 0.05 + Math.random() * 0.05,
        color: getGrassColor(currentTime)
      });
    }
    
    // Add bottom edge grass
    for (let i = 0; i < grassCount / 4; i++) {
      grassBlades.push({
        x: Math.random() * screenSize.width,
        baseY: screenSize.height + Math.random() * 50,
        height: 60 + Math.random() * 80,
        angle: 0,
        targetAngle: 0,
        width: 2 + Math.random() * 3,
        sway: Math.random() * Math.PI * 2,
        swaySpeed: 0.02 + Math.random() * 0.03,
        swayIntensity: 0.01 + Math.random() * 0.03,
        springiness: 0.05 + Math.random() * 0.05,
        color: `hsl(${100 + Math.random() * 30}, 70%, ${25 + Math.random() * 20}%)`
      });
    }
    
    setGrass(grassBlades);
  }, [screenSize, currentTime]);
  
  // Main animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    
    const animate = () => {
      ctx.clearRect(0, 0, screenSize.width, screenSize.height);
      
      // Draw sky gradient
      const skyGradient = ctx.createLinearGradient(0, 0, 0, screenSize.height);
      
      if (currentTime === 'dawn') {
        skyGradient.addColorStop(0, '#FF6B6B');
        skyGradient.addColorStop(0.3, '#FFB88C');
        skyGradient.addColorStop(0.7, '#FFE0B2');
        skyGradient.addColorStop(1, '#90CFA4');
      } else if (currentTime === 'morning') {
        skyGradient.addColorStop(0, '#87CEEB');
        skyGradient.addColorStop(0.7, '#B2EBF2');
        skyGradient.addColorStop(1, '#B9E3BD');
      } else if (currentTime === 'day') {
        skyGradient.addColorStop(0, '#4DA6FF');
        skyGradient.addColorStop(0.7, '#87CEEB');
        skyGradient.addColorStop(1, '#A1D7A9');
      } else if (currentTime === 'dusk') {
        skyGradient.addColorStop(0, '#FF8C42');
        skyGradient.addColorStop(0.3, '#FFA872');
        skyGradient.addColorStop(0.7, '#91A6B4');
        skyGradient.addColorStop(1, '#70997C');
      } else if (currentTime === 'evening') {
        skyGradient.addColorStop(0, '#355C7D');
        skyGradient.addColorStop(0.3, '#6C5B7B');
        skyGradient.addColorStop(0.7, '#C06C84');
        skyGradient.addColorStop(1, '#4A6F54');
      } else if (currentTime === 'night') {
        skyGradient.addColorStop(0, '#0B1A2A');
        skyGradient.addColorStop(0.3, '#183049');
        skyGradient.addColorStop(0.7, '#2A4D69');
        skyGradient.addColorStop(1, '#203A2E');
      }
      
      ctx.fillStyle = skyGradient;
      ctx.fillRect(0, 0, screenSize.width, screenSize.height);
      
      // Draw stars for night time
      if (currentTime === 'night') {
        if (!starsRef.current) {
          starsRef.current = [];
          for (let i = 0; i < 100; i++) {
            starsRef.current.push({
              x: Math.random() * screenSize.width,
              y: Math.random() * screenSize.height * 0.7,
              size: Math.random() * 1.5,
              opacity: Math.random() * 0.3 + 0.7,
              twinkleRate: Math.random() * 0.0005 + 0.0002
            });
          }
        }
        
        const timeNow = Date.now() * 0.001;
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(timeNow * star.twinkleRate) * 0.2 + 0.8;
          ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity * twinkle})`;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
          ctx.fill();
        });
      }
      
      // Draw moon for night/evening
      if (currentTime === 'night' || currentTime === 'evening') {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.beginPath();
        ctx.arc(screenSize.width * 0.8, screenSize.height * 0.2, 40, 0, Math.PI * 2);
        ctx.fill();
        
        // Moon shadow
        ctx.fillStyle = currentTime === 'night' ? '#0B1A2A' : '#355C7D';
        ctx.beginPath();
        ctx.arc(screenSize.width * 0.8 + 10, screenSize.height * 0.2, 40, 0, Math.PI * 2);
        ctx.fill();
      }
      
      // Draw sun for day/morning
      if (currentTime === 'day' || currentTime === 'morning') {
        ctx.fillStyle = '#FFD700';
        ctx.beginPath();
        ctx.arc(screenSize.width * 0.8, screenSize.height * 0.2, 40, 0, Math.PI * 2);
        ctx.fill();
        
        // Sun rays
        for (let i = 0; i < 12; i++) {
          const angle = (i * Math.PI * 2) / 12;
          ctx.beginPath();
          ctx.moveTo(
            screenSize.width * 0.8 + Math.cos(angle) * 50,
            screenSize.height * 0.2 + Math.sin(angle) * 50
          );
          ctx.lineTo(
            screenSize.width * 0.8 + Math.cos(angle) * 60,
            screenSize.height * 0.2 + Math.sin(angle) * 60
          );
          ctx.strokeStyle = '#FFD700';
          ctx.lineWidth = 3;
          ctx.stroke();
        }
      }
      
      // Update and draw grass
      grass.forEach(blade => {
        // Spring physics for interaction
        const angleDifference = blade.targetAngle - blade.angle;
        blade.angle += angleDifference * blade.springiness;
        
        // Natural swaying
        blade.sway += blade.swaySpeed;
        const naturalSway = Math.sin(blade.sway) * blade.swayIntensity;
        
        // Render grass blade
        ctx.save();
        ctx.translate(blade.x, blade.baseY);
        ctx.rotate(blade.angle + naturalSway);
        
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(
          blade.width / 2, -blade.height / 2,
          0, -blade.height
        );
        ctx.quadraticCurveTo(
          -blade.width / 2, -blade.height / 2,
          0, 0
        );
        
        ctx.fillStyle = blade.color;
        ctx.fill();
        ctx.restore();
      });
      
      // Draw floating discovery text
      if (phase === 'exploring') {
        floatingDiscoveries.forEach(discovery => {
          ctx.save();
          ctx.globalAlpha = discovery.opacity;
          ctx.font = `bold ${18 + discovery.scale * 6}px Arial`;
          
          let displayColor = discovery.color;
          if (discovery.color === '#4CAF50') {
            displayColor = '#388E3C';
          } else if (discovery.color === '#2196F3') {
            displayColor = '#1976D2';
          } else if (discovery.color === '#FFD700') {
            displayColor = '#B8860B';
          }
          
          ctx.fillStyle = displayColor;
          ctx.strokeStyle = 'white';
          ctx.lineWidth = 4;
          ctx.lineJoin = 'round';
          ctx.miterLimit = 2;
          ctx.textAlign = 'center';
          
          ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
          ctx.shadowBlur = 8;
          ctx.shadowOffsetX = 2;
          ctx.shadowOffsetY = 2;
          
          const textLines = discovery.text.split('\n');
          textLines.forEach((line, index) => {
            const yPosition = discovery.y + (index * 25);
            ctx.strokeText(line, discovery.x, yPosition);
            ctx.fillText(line, discovery.x, yPosition);
          });
          
          ctx.restore();
        });
      }
      
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [grass, screenSize, floatingDiscoveries, phase]);
  
  // Animate floating discoveries
  useEffect(() => {
    if (phase !== 'exploring') return;
    
    const floatInterval = setInterval(() => {
      setFloatingDiscoveries(prev => 
        prev.map(discovery => ({
          ...discovery,
          y: discovery.y - 1.5,
          opacity: discovery.opacity - 0.005,
          scale: discovery.scale + 0.01
        })).filter(discovery => discovery.opacity > 0)
      );
    }, 16);
    
    return () => clearInterval(floatInterval);
  }, [phase]);
  
  // Generate AI discovery
  const createAIDiscovery = async (x, y, rarity) => {
    if (isCreatingDiscovery) return;
    setIsCreatingDiscovery(true);
    
    try {
      let prompt;
      let itemColor;
      
      const randomSeed = Math.floor(Math.random() * 10000);
      
      // Time-specific examples
      let timeExamples = {
        common: [],
        uncommon: [],
        rare: []
      };
      
      switch (currentTime) {
        case 'dawn':
          timeExamples.common = ["a dew drop", "a spider web", "a morning newspaper"];
          timeExamples.uncommon = ["bird eggs", "a sunrise photo", "jogger's earbuds"];
          timeExamples.rare = ["a meteor fragment", "a rare dawn flower"];
          break;
        case 'morning':
          timeExamples.common = ["a coffee cup lid", "school supplies", "morning paper"];
          timeExamples.uncommon = ["breakfast remnants", "lost homework", "morning crow feather"];
          timeExamples.rare = ["a golden sunrise crystal", "morning glory seed"];
          break;
        case 'day':
          timeExamples.common = ["a bottle cap", "a lost button", "sandwich wrapper"];
          timeExamples.uncommon = ["sunglasses", "picnic blanket corner", "frisbee fragment"];
          timeExamples.rare = ["a sun-bleached artifact", "midday rainbow stone"];
          break;
        case 'dusk':
          timeExamples.common = ["a ticket stub", "evening newspaper page", "dog toy"];
          timeExamples.uncommon = ["sunset photo", "evening jogger's headband", "dusk-blooming petal"];
          timeExamples.rare = ["a sunset agate", "twilight moth wing"];
          break;
        case 'evening':
          timeExamples.common = ["a dinner napkin", "restaurant receipt", "evening commuter pass"];
          timeExamples.uncommon = ["evening party invite", "concert ticket stub", "lost dinner reservation"];
          timeExamples.rare = ["a star emerald", "evening primrose seed"];
          break;
        case 'night':
          timeExamples.common = ["a glow stick", "flashlight battery", "night owl feather"];
          timeExamples.uncommon = ["moonstone chip", "nocturnal flower petal", "stargazer's map piece"];
          timeExamples.rare = ["a fallen star fragment", "lunar crystal", "night bloom essence"];
          break;
      }
      
      // Location-specific context
      let locationContext = '';
      let commonItems = [];
      let uncommonItems = [];
      let rareItems = [];
      
      if (explorePlaceName) {
        const placeLower = explorePlaceName.toLowerCase();
        
        if (placeLower.includes('soccer') || placeLower.includes('football')) {
          locationContext = ' in soccer field grass';
          commonItems = ["a missing cleat stud", "a torn goal net thread", "a grass-stained shin guard strap", "a referee's dropped whistle"];
          uncommonItems = ["a lost team captain's armband", "a piece of championship confetti", "a section of penalty box line chalk"];
          rareItems = ["a player's lucky pre-game penny", "a World Cup final ticket stub", "a signed soccer card"];
        } else if (placeLower.includes('backyard') || placeLower.includes('back yard')) {
          locationContext = ' in backyard grass';
          commonItems = ["a dropped clothes pin", "a lost earring back", "a pet collar tag", "a barbecue skewer"];
          uncommonItems = ["a child's lost tooth", "a wedding ring", "a buried dog toy"];
          rareItems = ["a 1950s soda bottle cap", "grandmother's lost thimble", "a time capsule corner"];
        } else if (placeLower.includes('golf')) {
          locationContext = ' in golf course grass';
          commonItems = ["a broken tee", "a lost ball marker", "a scorecard pencil", "a divot repair tool"];
          uncommonItems = ["a pro's ball marker", "a clubhouse member pin", "a yardage book page"];
          rareItems = ["a master's tournament ball", "Arnold Palmer's cigar tip", "a hole-in-one commemorative coin"];
        } else if (placeLower.includes('school') || placeLower.includes('playground')) {
          locationContext = ' in school playground grass';
          commonItems = ["a lunch money quarter", "a broken pencil tip", "a hair tie", "a Pokemon card"];
          uncommonItems = ["a retainer", "a class ring", "a report card corner"];
          rareItems = ["a 1980s lunch token", "a vintage marble shooter", "a class of '99 pin"];
        } else if (placeLower.includes('picnic')) {
          locationContext = ' in picnic area grass';
          commonItems = ["a plastic fork tine", "a bottle cap", "a napkin corner", "a watermelon seed"];
          uncommonItems = ["a wine cork", "a picnic blanket tag", "a forgotten corkscrew"];
          rareItems = ["a proposal ring box hinge", "a vintage thermos lid", "a 1960s soda pull tab"];
        } else if (placeLower.includes('meadow')) {
          locationContext = ' in meadow grass';
          commonItems = ["a rabbit dropping", "a bird feather", "a dried flower head", "an acorn cap"];
          uncommonItems = ["an arrowhead", "a deer antler tip", "a snake skin piece"];
          rareItems = ["a fossil impression", "a natural crystal", "a gold nugget fragment", "an ancient pottery shard", "a meteorite piece"];
        } else if (placeLower.includes('park')) {
          locationContext = ' in park grass';
          commonItems = ["a dog tag", "a frisbee chip", "a tennis ball fuzz", "a picnic fork"];
          uncommonItems = ["a lost earring", "a festival wristband", "a skateboard wheel"];
          rareItems = ["a 1920s jazz pin", "a vintage arcade token", "an antique carousel charm", "a famous writer's lost pen cap"];
        } else if (placeLower.includes('singapore') || placeLower.includes('botanical gardens')) {
          locationContext = ' in Singapore botanical garden grass';
          commonItems = ["a tropical flower petal", "a orchid leaf", "a tourist ticket stub", "a garden map fragment"];
          uncommonItems = ["a heritage tree plaque piece", "a bonsai exhibition tag", "a bird watching notebook page"];
          rareItems = ["a Raffles-era trade coin", "a WWII currency piece", "a spice trader's ancient bead", "a rare orchid seed pod"];
        } else if (placeLower.includes('central park') || placeLower.includes('new york')) {
          locationContext = ' in Central Park grass';
          commonItems = ["a hot dog wrapper", "a metro card", "a tourist map piece", "a horse carriage bolt"];
          uncommonItems = ["a Broadway ticket stub", "a Yankees cap button", "a film location marker"];
          rareItems = ["a 1920s speakeasy token", "a legendary performer's button", "a vintage subway token", "an art deco period charm"];
        } else if (placeLower.includes('tokyo') || placeLower.includes('imperial')) {
          locationContext = ' in Tokyo Imperial Garden grass';
          commonItems = ["a cherry blossom petal", "a crane feather", "a koi food pellet", "a bamboo leaf"];
          uncommonItems = ["a tea ceremony ticket", "a kimono fabric swatch", "a garden stone fragment"];
          rareItems = ["an Edo period coin", "a vintage samurai button", "a traditional craft tool piece", "a rare jade fragment"];
        } else if (placeLower.includes('hyde park') || placeLower.includes('london')) {
          locationContext = ' in Hyde Park grass';
          commonItems = ["a pigeon feather", "a speaker's corner badge", "a royal parks map piece", "a swan feather"];
          uncommonItems = ["a palace guard button", "a rowing club pin", "a speaker's corner plaque fragment"];
          rareItems = ["a Victorian jewelry piece", "a literary society pin", "a rare royal commemorative coin", "an antique theater token"];
        } else {
          locationContext = ` in ${explorePlaceName} grass`;
          commonItems = ["a bottle cap", "a coin", "a button", "a plastic wrapper piece"];
          uncommonItems = ["a key", "a ring", "a zipper pull", "a earring"];
          rareItems = ["an antique coin", "a vintage toy piece", "a lost heirloom"];
        }
      } else {
        locationContext = ' in grass';
        commonItems = ["a bottle cap", "a coin", "a button", "a plastic wrapper piece"];
        uncommonItems = ["a key", "a ring", "a zipper pull", "a earring"];
        rareItems = ["an antique coin", "a vintage toy piece", "a lost heirloom"];
      }
      
      if (rarity < 0.7) {
        // Common items
        const examples = [...commonItems, ...timeExamples.common];
        const example = examples[Math.floor(Math.random() * examples.length)];
        prompt = `Generate a common, realistic object someone would actually find${locationContext} during ${currentTime}. 2-4 words. Include "a" or "an". Lowercase. Example: "${example}". Be very specific to the location and time. Seed: ${randomSeed}`;
        itemColor = '#4CAF50';
      } else if (rarity < 0.9) {
        // Uncommon items
        const examples = [...uncommonItems, ...timeExamples.uncommon];
        const example = examples[Math.floor(Math.random() * examples.length)];
        prompt = `Generate an uncommon but real object someone might find${locationContext} during ${currentTime}. 2-5 words. Include "a" or "an". Lowercase. Example: "${example}". Must be actually findable in that location at this time. Seed: ${randomSeed}`;
        itemColor = '#2196F3';
      } else {
        // Rare items
        const examples = [...rareItems, ...timeExamples.rare];
        const example = examples[Math.floor(Math.random() * examples.length)];
        prompt = `Generate a rare but real object someone could find${locationContext} during ${currentTime}. 2-5 words. Lowercase. Example: "${example}". Should be exciting or unusual - could be historical, natural wonder, valuable, or whimsical. Consider the time of day. Seed: ${randomSeed}`;
        itemColor = '#FFD700';
      }
      
      // Avoid recent duplicates
      const recentItems = lastFoundItems.slice(-3);
      let finalPrompt = prompt;
      if (recentItems.length > 0) {
        finalPrompt += ` Avoid these recent discoveries: "${recentItems.join('", "')}". Generate something different.`;
      }
      
      const response = await window.claude.complete(finalPrompt);
      const cleanedResponse = response.trim().toLowerCase();
      
      // Check for repetition limit
      const currentCount = itemHistory[cleanedResponse] || 0;
      if (currentCount >= 3) {
        // Try again with different item
        const retryPrompt = prompt + ` Avoid: "${cleanedResponse}". Also avoid these recent discoveries: "${lastFoundItems.join('", "')}". Generate something completely different.`;
        const retryResponse = await window.claude.complete(retryPrompt);
        const retryCleanedResponse = retryResponse.trim().toLowerCase();
        
        // Update tracking
        setItemHistory(prev => ({
          ...prev,
          [retryCleanedResponse]: (prev[retryCleanedResponse] || 0) + 1
        }));
        
        setLastFoundItems(prev => [...prev, retryCleanedResponse].slice(-5));
        
        // Add to found items
        setFoundItems(prev => [...prev, {
          text: retryCleanedResponse,
          color: itemColor,
          time: secondsOutside,
          rarity: rarity < 0.7 ? 'common' : rarity < 0.9 ? 'uncommon' : 'rare'
        }]);
        
        showDiscoveryText(retryCleanedResponse, x, y, itemColor);
        playFoundSound(rarity);
      } else {
        // Use original response
        setItemHistory(prev => ({
          ...prev,
          [cleanedResponse]: currentCount + 1
        }));
        
        setLastFoundItems(prev => [...prev, cleanedResponse].slice(-5));
        
        setFoundItems(prev => [...prev, {
          text: cleanedResponse,
          color: itemColor,
          time: secondsOutside,
          rarity: rarity < 0.7 ? 'common' : rarity < 0.9 ? 'uncommon' : 'rare'
        }]);
        
        showDiscoveryText(cleanedResponse, x, y, itemColor);
        playFoundSound(rarity);
      }
    } catch (error) {
      console.error('Error generating discovery:', error);
      const fallbackItems = [
        t('tinyTreasure'),
        t('smallWonder'),
        t('somethingSpecial'),
        t('curiousFind'),
        t('hiddenGem')
      ];
      const fallback = fallbackItems[Math.floor(Math.random() * fallbackItems.length)];
      
      setFloatingDiscoveries(prev => [...prev, {
        text: t('youFoundText').replace('{item}', fallback),
        x: x,
        y: y - 60,
        opacity: 1,
        scale: 0,
        color: '#9C27B0'
      }]);
    } finally {
      setTimeout(() => setIsCreatingDiscovery(false), 200);
    }
  };
  
  // Display discovery text
  const showDiscoveryText = (text, x, y, color) => {
    const maxLength = 20;
    let displayText = text;
    if (text.length > maxLength) {
      const words = text.split(' ');
      let firstLine = [];
      let secondLine = [];
      let currentLine = firstLine;
      
      words.forEach(word => {
        if (currentLine === firstLine && firstLine.join(' ').length + word.length > maxLength) {
          currentLine = secondLine;
        }
        currentLine.push(word);
      });
      
      displayText = firstLine.join(' ') + '\n' + secondLine.join(' ');
    }
    
    // Keep text on screen
    let xPosition = x;
    const padding = 150;
    if (xPosition < padding) xPosition = padding;
    if (xPosition > screenSize.width - padding) xPosition = screenSize.width - padding;
    
    setFloatingDiscoveries(prev => [...prev, {
      text: t('youFoundText').replace('{item}', displayText),
      x: xPosition,
      y: y - 60,
      opacity: 1,
      scale: 0,
      color: color
    }]);
  };
  
  // Handle mouse/touch interaction
  const handleGrassInteraction = (e) => {
    if (phase !== 'exploring') return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Check for discoveries
    if (hiddenSpots && hiddenSpots.length > 0) {
      hiddenSpots.forEach((spot, index) => {
        if (!spot.found) {
          const distance = Math.hypot(spot.x - x, spot.y - y);
          if (distance < 50) {
            createAIDiscovery(spot.x, spot.y, spot.rarity);
            
            // Replace with new spot
            const newSpots = [...hiddenSpots];
            const margin = 100;
            newSpots[index] = {
              x: margin + Math.random() * (screenSize.width - 2 * margin),
              y: screenSize.height - 10 - Math.random() * 150,
              found: false,
              rarity: Math.random()
            };
            setHiddenSpots(newSpots);
          }
        }
      });
    }
    
    // Update grass physics
    const newGrass = grass.map(blade => {
      const distance = Math.hypot(blade.x - x, blade.baseY - y);
      const radius = 100;
      
      if (distance < radius) {
        const strength = (radius - distance) / radius;
        const dx = blade.x - x;
        const angle = Math.atan2(dx, 50) * strength * 0.5;
        
        return {
          ...blade,
          targetAngle: angle
        };
      }
      
      return {
        ...blade,
        targetAngle: 0
      };
    });
    
    setGrass(newGrass);
  };
  
  const handleMouseLeave = () => {
    const newGrass = grass.map(blade => ({
      ...blade,
      targetAngle: 0
    }));
    setGrass(newGrass);
  };
  
  const startExploration = () => {
    // Enable audio on user interaction
    if (soundContext && soundContext.state === 'suspended') {
      soundContext.resume();
    }
    
    setTransitioning(true);
    setTimeout(() => {
      setPhase('exploring');
      setIsTimerRunning(true);
      setTransitioning(false);
    }, 500);
  };
  
  const returnInside = () => {
    setTransitioning(true);
    setTimeout(() => {
      setPhase('results');
      setIsTimerRunning(false);
      setTransitioning(false);
    }, 500);
  };
  
  const restartAdventure = () => {
    setTransitioning(true);
    setTimeout(() => {
      setPhase('welcome');
      setSecondsOutside(0);
      setFoundItems([]);
      setFloatingDiscoveries([]);
      setExplorePlaceName('');
      setItemHistory({});
      setLastFoundItems([]);
      setTransitioning(false);
    }, 500);
  };
  
  return (
    <div className="fixed inset-0 overflow-hidden">
      {/* Grass canvas background */}
      <canvas
        ref={canvasRef}
        width={screenSize.width}
        height={screenSize.height}
        className="absolute inset-0 cursor-pointer"
        onMouseMove={handleGrassInteraction}
        onTouchMove={(e) => {
          e.preventDefault();
          handleGrassInteraction(e.touches[0]);
        }}
        onMouseLeave={handleMouseLeave}
        onTouchEnd={handleMouseLeave}
      />
      
      {/* Welcome screen */}
      {phase === 'welcome' && (
        <div className={`absolute inset-0 flex items-center justify-center ${currentTime === 'night' ? 'bg-black/20' : 'bg-black/5'} backdrop-blur-md transition-opacity duration-500 ${transitioning ? 'opacity-0' : 'opacity-100'}`}>
          <div className="text-center p-8 bg-white/40 backdrop-blur-lg rounded-3xl shadow-2xl max-w-md mx-4 transform transition-all duration-500 hover:scale-105 border border-white/40">
            <h1 className={`text-4xl font-light mb-8 ${currentTime === 'night' ? 'text-white' : 'text-gray-700'} tracking-tight`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
              {t('stepOutsideTitle')}
            </h1>
            <p className={`text-lg ${currentTime === 'night' ? 'text-gray-200' : 'text-gray-600'} mb-6 leading-relaxed font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
              {currentTime === 'night' 
                ? t('nightGrassSecrets')
                : currentTime === 'dawn'
                ? t('dawnBreaksSecrets')
                : currentTime === 'evening'
                ? t('eveningSettlesSecrets')
                : currentTime === 'dusk'
                ? t('twilightTransforms')
                : t('magicWaitingGrass')}
            </p>
            
            <div className="mb-8">
              <div className="relative">
                <input
                  type="text"
                  value={explorePlaceName}
                  onChange={(e) => setExplorePlaceName(e.target.value)}
                  placeholder={t('whereExploreInput')}
                  className={`w-full px-4 py-3 text-center bg-white/30 border border-white/40 rounded-full ${currentTime === 'night' ? 'text-gray-700 placeholder-gray-500' : 'text-gray-700 placeholder-gray-500'} focus:outline-none focus:ring-2 focus:ring-white/40 backdrop-blur-md font-light`}
                  style={{ fontFamily: 'Quicksand, sans-serif' }}
                />
                <button
                  onClick={pickRandomPlace}
                  className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 text-gray-600 hover:text-gray-800 transition-colors duration-200`}
                  title={t('shuffleLocationTitle')}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            
            <button 
              onClick={startExploration}
              className="bg-white/50 backdrop-blur-md hover:bg-white/60 text-gray-700 font-medium py-4 px-8 rounded-full text-xl shadow-lg transform transition-all duration-300 hover:shadow-xl hover:-translate-y-1 active:translate-y-0 border border-white/40"
              style={{ fontFamily: 'Quicksand, sans-serif' }}
            >
              {t('goTouchGrassButton')}
            </button>
          </div>
        </div>
      )}
      
      {/* Exploration interface */}
      {phase === 'exploring' && (
        <div className={`absolute top-6 left-6 bg-white/40 backdrop-blur-md rounded-2xl p-5 shadow-xl transform transition-all duration-300 hover:scale-105 border border-white/40 ${transitioning ? 'opacity-0' : 'opacity-100'}`}>
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-white/50 rounded-full p-3">
              <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('timeOutsideLabel')}</p>
              <p className={`text-2xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{formatTimer(secondsOutside)}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-white/50 rounded-full p-3">
              <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {currentTime === 'night' || currentTime === 'evening' ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                )}
              </svg>
            </div>
            <div>
              <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('timeOfDayLabel')}</p>
              <p className={`text-xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
                {currentTime === 'dawn' ? t('dawnTimeOfDay') :
                 currentTime === 'morning' ? t('morningTimeOfDay') :
                 currentTime === 'day' ? t('dayTimeOfDay') :
                 currentTime === 'dusk' ? t('duskTimeOfDay') :
                 currentTime === 'evening' ? t('eveningTimeOfDay') :
                 t('nightTimeOfDay')}
              </p>
            </div>
          </div>
          
          {explorePlaceName && (
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-white/50 rounded-full p-3">
                <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('locationLabel')}</p>
                <p className={`text-xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{explorePlaceName}</p>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-white/50 rounded-full p-3">
              <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div>
              <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('discoveriesLabel')}</p>
              <p className={`text-2xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{foundItems.length}</p>
            </div>
          </div>
          
          <button 
            onClick={returnInside}
            className="w-full bg-white/50 backdrop-blur-md hover:bg-white/60 text-gray-700 font-medium py-3 px-6 rounded-xl shadow-md transform transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 border border-white/40"
            style={{ fontFamily: 'Quicksand, sans-serif' }}
          >
            {t('goBackInsideButton')}
          </button>
        </div>
      )}
      
      {/* Results screen */}
      {phase === 'results' && (
        <div className={`absolute inset-0 flex items-center justify-center ${currentTime === 'night' ? 'bg-black/20' : 'bg-black/5'} backdrop-blur-md transition-opacity duration-500 ${transitioning ? 'opacity-0' : 'opacity-100'}`}>
          <div className="bg-white/40 backdrop-blur-lg rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all duration-500 border border-white/40">
            <h2 className={`text-3xl font-light mb-6 ${currentTime === 'night' ? 'text-white' : 'text-gray-700'} text-center`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
              {explorePlaceName ? t('locationGrassAdventureTitle').replace('{location}', explorePlaceName) : t('grassAdventureTitle')}
            </h2>
            
            <div className="flex justify-between mb-8 p-4 bg-white/20 rounded-xl">
              <div className="text-center flex-1">
                <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} uppercase tracking-wider font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('timeOutsideLabel')}</p>
                <p className={`text-2xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'} pl-4`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{formatTimer(secondsOutside)}</p>
              </div>
              <div className="w-px bg-white/30"></div>
              <div className="text-center flex-1">
                <p className={`text-sm ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-600'} uppercase tracking-wider font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('discoveriesLabel')}</p>
                <p className={`text-2xl font-normal ${currentTime === 'night' ? 'text-white' : 'text-gray-700'} pr-4`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{foundItems.length}</p>
              </div>
            </div>
            
            <div className="mb-8">
              <h3 className={`font-medium mb-4 ${currentTime === 'night' ? 'text-white' : 'text-gray-700'} text-lg`} style={{ fontFamily: 'Quicksand, sans-serif' }}>{t('yourDiscoveriesTitle')}</h3>
              <div className="max-h-64 overflow-y-auto bg-white/20 rounded-xl p-4 shadow-inner">
                {foundItems.length === 0 ? (
                  <div className="text-center py-8">
                    <p className={`${currentTime === 'night' ? 'text-gray-200' : 'text-gray-600'} font-light`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
                      {t('professionalGrassAvoider')}
                    </p>
                  </div>
                ) : (
                  <>
                    {['rare', 'uncommon', 'common'].map(rarityType => {
                      const rarityItems = foundItems.filter(item => item.rarity === rarityType);
                      if (rarityItems.length === 0) return null;
                      
                      return (
                        <div key={rarityType} className="mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            {rarityType === 'rare' && (
                              <span className={`text-sm font-light ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-500'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
                                {t('rareFinds')}
                              </span>
                            )}
                            {rarityType === 'uncommon' && (
                              <span className={`text-sm font-light ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-500'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
                                {t('uncommonFinds')}
                              </span>
                            )}
                            {rarityType === 'common' && (
                              <span className={`text-sm font-light ${currentTime === 'night' ? 'text-gray-300' : 'text-gray-500'}`} style={{ fontFamily: 'Quicksand, sans-serif' }}>
                                {t('commonFinds')}
                              </span>
                            )}
                          </div>
                          
                          {rarityItems.map((item, index) => (
                            <div 
                              key={index} 
                              className={`mb-2 p-3 rounded-lg backdrop-blur-sm shadow-sm transform transition-all duration-300 hover:scale-102 flex items-center justify-between ${
                                rarityType === 'rare' ? 'bg-yellow-100/40 hover:bg-yellow-100/60' :
                                rarityType === 'uncommon' ? 'bg-blue-100/40 hover:bg-blue-100/60' :
                                'bg-green-100/40 hover:bg-green-100/60'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <span className="font-normal text-gray-700" style={{ fontFamily: 'Quicksand, sans-serif' }}>
                                  {item.text}
                                </span>
                              </div>
                              <span className="text-gray-500 text-sm ml-2 font-light" style={{ fontFamily: 'Quicksand, sans-serif' }}>
                                {formatTimer(item.time)}
                              </span>
                            </div>
                          ))}
                        </div>
                      );
                    })}
                  </>
                )}
              </div>
            </div>
            
            <button 
              onClick={restartAdventure}
              className="w-full bg-white/50 backdrop-blur-md hover:bg-white/60 text-gray-700 font-medium py-3 px-6 rounded-full shadow-lg transform transition-all duration-300 hover:shadow-xl hover:-translate-y-1 active:translate-y-0 border border-white/40"
              style={{ fontFamily: 'Quicksand, sans-serif' }}
            >
              {t('goOutsideAgainButton')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TouchGrassGame;