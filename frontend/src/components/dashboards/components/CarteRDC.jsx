import React, { useState } from 'react';

// Simplified SVG paths for DRC's 26 provinces
// Approximate boundaries for visual representation
const PROVINCES_PATHS = {
  "Kinshasa": { d: "M 168 385 L 173 380 L 178 383 L 176 389 L 170 390 Z", cx: 173, cy: 385 },
  "Kongo-Central": { d: "M 135 370 L 165 355 L 175 375 L 170 395 L 150 400 L 130 395 L 125 380 Z", cx: 150, cy: 378 },
  "Kwango": { d: "M 175 375 L 210 350 L 230 370 L 225 410 L 195 420 L 170 395 Z", cx: 200, cy: 387 },
  "Kwilu": { d: "M 210 330 L 240 310 L 260 330 L 255 370 L 230 370 L 210 350 Z", cx: 235, cy: 340 },
  "Mai-Ndombe": { d: "M 220 260 L 255 250 L 270 280 L 260 330 L 240 310 L 210 330 L 195 300 Z", cx: 240, cy: 290 },
  "Equateur": { d: "M 215 175 L 255 160 L 280 180 L 275 230 L 255 250 L 220 260 L 200 230 L 205 195 Z", cx: 240, cy: 210 },
  "Mongala": { d: "M 255 160 L 300 130 L 330 145 L 320 180 L 290 195 L 280 180 Z", cx: 295, cy: 165 },
  "Nord-Ubangi": { d: "M 255 100 L 300 80 L 340 95 L 330 130 L 300 130 L 270 115 Z", cx: 300, cy: 108 },
  "Sud-Ubangi": { d: "M 215 140 L 255 100 L 270 115 L 255 160 L 215 175 L 200 160 Z", cx: 237, cy: 140 },
  "Tshuapa": { d: "M 280 180 L 320 180 L 340 210 L 330 250 L 305 260 L 275 230 Z", cx: 308, cy: 220 },
  "Tshopo": { d: "M 330 145 L 380 120 L 415 140 L 410 190 L 380 210 L 340 210 L 320 180 Z", cx: 370, cy: 170 },
  "Bas-Uélé": { d: "M 340 95 L 395 75 L 430 95 L 415 140 L 380 120 L 330 130 Z", cx: 385, cy: 108 },
  "Haut-Uélé": { d: "M 395 75 L 450 55 L 490 70 L 480 110 L 450 130 L 430 95 Z", cx: 450, cy: 90 },
  "Ituri": { d: "M 450 130 L 480 110 L 510 120 L 515 165 L 490 185 L 460 170 L 450 145 Z", cx: 480, cy: 148 },
  "Nord-Kivu": { d: "M 460 170 L 490 185 L 500 220 L 490 260 L 470 250 L 455 220 L 450 195 Z", cx: 475, cy: 215 },
  "Sud-Kivu": { d: "M 455 260 L 490 260 L 495 310 L 475 330 L 455 310 L 445 285 Z", cx: 470, cy: 292 },
  "Maniema": { d: "M 380 210 L 410 190 L 450 195 L 455 260 L 445 285 L 410 300 L 380 280 L 365 250 Z", cx: 415, cy: 245 },
  "Sankuru": { d: "M 305 260 L 365 250 L 380 280 L 370 320 L 335 330 L 300 310 Z", cx: 340, cy: 290 },
  "Kasai": { d: "M 255 280 L 305 260 L 300 310 L 280 335 L 255 330 L 240 310 Z", cx: 273, cy: 303 },
  "Kasai-Central": { d: "M 280 335 L 300 310 L 335 330 L 325 365 L 295 375 L 270 355 Z", cx: 300, cy: 347 },
  "Kasai-Oriental": { d: "M 335 330 L 370 320 L 385 345 L 375 380 L 345 385 L 325 365 Z", cx: 355, cy: 355 },
  "Lomami": { d: "M 370 320 L 410 300 L 430 330 L 420 370 L 395 385 L 375 380 L 385 345 Z", cx: 400, cy: 348 },
  "Haut-Lomami": { d: "M 395 385 L 420 370 L 445 390 L 450 430 L 425 450 L 395 440 L 380 415 Z", cx: 418, cy: 415 },
  "Lualaba": { d: "M 345 385 L 375 380 L 395 385 L 380 415 L 395 440 L 370 460 L 340 445 L 330 415 Z", cx: 363, cy: 420 },
  "Haut-Katanga": { d: "M 425 450 L 450 430 L 490 440 L 500 480 L 475 505 L 440 500 L 415 480 Z", cx: 458, cy: 470 },
  "Tanganyika": { d: "M 430 330 L 455 310 L 475 330 L 490 370 L 490 440 L 450 430 L 445 390 L 420 370 Z", cx: 460, cy: 380 },
};

// Color scale based on number of educational provinces
const getColor = (count) => {
  if (count >= 5) return '#312e81'; // indigo-900
  if (count >= 3) return '#4338ca'; // indigo-700
  if (count >= 2) return '#6366f1'; // indigo-500
  return '#a5b4fc'; // indigo-300
};

const CarteRDC = ({ provincesData, onSelectProvince }) => {
  const [hoveredProvince, setHoveredProvince] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e, provinceName) => {
    const rect = e.currentTarget.closest('svg').getBoundingClientRect();
    setTooltipPos({ x: e.clientX - rect.left, y: e.clientY - rect.top - 10 });
    setHoveredProvince(provinceName);
  };

  const getProvinceData = (name) => {
    return provincesData.find(p => p.provinceAdmin === name);
  };

  return (
    <div className="relative bg-white rounded-xl shadow-sm border border-gray-200 p-4" data-testid="carte-rdc">
      <h3 className="text-lg font-bold text-gray-900 mb-2 text-center">Carte des Provinces de la RDC</h3>
      <p className="text-xs text-gray-500 text-center mb-3">Cliquez sur une province pour voir ses provinces educationnelles</p>
      
      <div className="relative mx-auto" style={{ maxWidth: '700px' }}>
        <svg
          viewBox="110 40 430 500"
          className="w-full h-auto"
          data-testid="carte-svg"
        >
          {/* Background */}
          <rect x="110" y="40" width="430" height="500" fill="#f0f9ff" rx="8" />
          
          {/* Province paths */}
          {Object.entries(PROVINCES_PATHS).map(([name, path]) => {
            const data = getProvinceData(name);
            const nbPE = data?.provincesEdu?.length || 0;
            const isHovered = hoveredProvince === name;
            
            return (
              <g key={name}>
                <path
                  d={path.d}
                  fill={getColor(nbPE)}
                  stroke={isHovered ? '#fbbf24' : '#e0e7ff'}
                  strokeWidth={isHovered ? 2.5 : 1}
                  className="cursor-pointer transition-all duration-150"
                  style={{ opacity: isHovered ? 1 : 0.85, filter: isHovered ? 'brightness(1.2)' : 'none' }}
                  onMouseMove={(e) => handleMouseMove(e, name)}
                  onMouseLeave={() => setHoveredProvince(null)}
                  onClick={() => data && onSelectProvince(data)}
                  data-testid={`carte-province-${name.toLowerCase().replace(/[^a-z]/g, '-')}`}
                />
                {/* Province label */}
                <text
                  x={path.cx}
                  y={path.cy}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize={name === 'Kinshasa' ? '6' : '7'}
                  fontWeight="600"
                  className="pointer-events-none select-none"
                  style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}
                >
                  {name.length > 12 ? name.substring(0, 10) + '..' : name}
                </text>
                <text
                  x={path.cx}
                  y={path.cy + 10}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#c7d2fe"
                  fontSize="6"
                  className="pointer-events-none select-none"
                >
                  {nbPE} P.E.
                </text>
              </g>
            );
          })}
        </svg>

        {/* Tooltip */}
        {hoveredProvince && (
          <div
            className="absolute z-10 bg-gray-900 text-white rounded-lg px-3 py-2 text-xs pointer-events-none shadow-xl"
            style={{ left: tooltipPos.x, top: tooltipPos.y, transform: 'translate(-50%, -100%)' }}
            data-testid="carte-tooltip"
          >
            {(() => {
              const data = getProvinceData(hoveredProvince);
              const nbPE = data?.provincesEdu?.length || 0;
              const nbSD = data?.provincesEdu?.reduce((a, pe) => a + pe.sousDivisions.length, 0) || 0;
              return (
                <div>
                  <p className="font-bold text-sm">{hoveredProvince}</p>
                  <p className="text-gray-300">{nbPE} province(s) educationnelle(s)</p>
                  <p className="text-gray-300">{nbSD} sous-division(s)</p>
                </div>
              );
            })()}
          </div>
        )}
      </div>

      {/* Légende */}
      <div className="flex justify-center gap-4 mt-3 flex-wrap">
        {[
          { color: '#a5b4fc', label: '1 P.E.' },
          { color: '#6366f1', label: '2 P.E.' },
          { color: '#4338ca', label: '3 P.E.' },
          { color: '#312e81', label: '5+ P.E.' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded" style={{ backgroundColor: item.color }} />
            <span className="text-xs text-gray-600">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CarteRDC;
