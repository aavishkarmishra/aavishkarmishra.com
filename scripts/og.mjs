import sharp from 'sharp';

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <rect width="1200" height="630" fill="#fdfdfb"/>
  <rect x="0" y="0" width="1200" height="8" fill="#9c3d1e"/>

  <path d="M92 214 L124 158 L156 214" fill="none" stroke="#1b1b19"
        stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="124" cy="158" r="8" fill="#9c3d1e"/>

  <text x="92" y="326" font-family="Helvetica Neue, Helvetica, Arial"
        font-size="76" font-weight="600" fill="#1b1b19">Aavishkar Mishra</text>

  <text x="92" y="400" font-family="Georgia, serif" font-size="34" fill="#4a4945">
    Full-stack engineer. Idea to production,
  </text>
  <text x="92" y="446" font-family="Georgia, serif" font-size="34" fill="#4a4945">
    and answerable for what happens after.
  </text>

  <text x="92" y="556" font-family="Helvetica Neue, Helvetica, Arial"
        font-size="24" fill="#93928a">aavishkarmishra.com</text>
</svg>`;

await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toFile('public/og.png');
console.log('wrote public/og.png');
