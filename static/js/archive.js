const FEATURED = JSON.parse(document.getElementById('featured-data').textContent);
    const ENTRIES_DATA = JSON.parse(document.getElementById('entries-data').textContent);
    let COLLECTIONS = JSON.parse(document.getElementById('collections-data').textContent);
    const BW = 170, BH = 240, SW = 18;

    function darken(hex, n) {
        const x = parseInt(hex.replace("#", ""), 16);
        const r = Math.max(0, (x >> 16) - n);
        const g = Math.max(0, ((x >> 8) & 0xff) - n);
        const b = Math.max(0, (x & 0xff) - n);
        return `rgb(${r},${g},${b})`;
    }

    function generateSVG(art, bg) {
        const darkBg = darken(bg, 40);
        const linenLines = Array.from({ length: Math.ceil(BH / 8) + 1 }, (_, i) => `<line x1="0" y1="${i * 8 + 6}" x2="${BW}" y2="${i * 8 + 6}" stroke="#D4CCBA" stroke-width="0.6" opacity="0.6" />`).join('');
        const woodPaths = Array.from({ length: 14 }, (_, i) => {
            const y = i * 16 + 8;
            const w = Math.sin(i * 0.78) * 5;
            return `<path d="M0,${y} C52,${y + w} 102,${y - w} ${BW},${y + w / 2}" stroke="#2C1C0A" stroke-width="2.5" fill="none" opacity="0.75" />`;
        }).join('');

        const switchCase = {
            'botanical': `
                <svg width="${BW}" height="${BH}" viewBox="0 0 ${BW} ${BH}" xmlns="http://www.w3.org/2000/svg">
                    <rect width="${BW}" height="${BH}" fill="${bg}" />
                    <rect width="${SW}" height="${BH}" fill="${darkBg}" />
                    <ellipse cx="44" cy="107" rx="26" ry="46" fill="#6A9040" transform="rotate(-18 44 107)" />
                    <ellipse cx="77" cy="82" rx="20" ry="38" fill="#8AAA58" transform="rotate(12 77 82)" />
                    <ellipse cx="112" cy="118" rx="23" ry="42" fill="#6A9040" transform="rotate(-8 112 118)" />
                    <line x1="44" y1="140" x2="44" y2="190" stroke="#4A7028" stroke-width="1.8" />
                    <line x1="77" y1="115" x2="77" y2="190" stroke="#4A7028" stroke-width="1.8" />
                    <line x1="112" y1="152" x2="112" y2="190" stroke="#4A7028" stroke-width="1.8" />
                </svg>`,
            'linen': `
                <svg width="${BW}" height="${BH}" viewBox="0 0 ${BW} ${BH}" xmlns="http://www.w3.org/2000/svg">
                    <rect width="${BW}" height="${BH}" fill="${bg}" />
                    <rect width="${SW}" height="${BH}" fill="${darken(bg, 35)}" />
                    ${linenLines}
                </svg>`,
            'face': `
                <svg width="${BW}" height="${BH}" viewBox="0 0 ${BW} ${BH}" xmlns="http://www.w3.org/2000/svg">
                    <rect width="${BW}" height="${BH}" fill="${bg}" />
                    <rect width="${SW}" height="${BH}" fill="${darkBg}" />
                    <ellipse cx="77" cy="80" rx="34" ry="40" fill="#1E0E06" />
                    <ellipse cx="77" cy="148" rx="28" ry="34" fill="#E07828" />
                    <circle cx="64" cy="68" r="6" fill="#B84818" />
                    <circle cx="90" cy="71" r="6" fill="#B84818" />
                    <path d="M63 92 Q77 104 91 92" stroke="#3C1808" stroke-width="2.5" fill="none" stroke-linecap="round" />
                </svg>`,
            'wood': `
                <svg width="${BW}" height="${BH}" viewBox="0 0 ${BW} ${BH}" xmlns="http://www.w3.org/2000/svg">
                    <rect width="${BW}" height="${BH}" fill="${bg}" />
                    ${woodPaths}
                </svg>`,
            'clouds': `
                <svg width="${BW}" height="${BH}" viewBox="0 0 ${BW} ${BH}" xmlns="http://www.w3.org/2000/svg">
                    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#C8E4F8" /><stop offset="100%" stop-color="#88B8E0" /></linearGradient>
                    <rect width="${BW}" height="${BH}" fill="url(#skyGrad)" />
                    <rect width="${SW}" height="${BH}" fill="${darken(bg, 38)}" />
                    <ellipse cx="52" cy="78" rx="36" ry="20" fill="white" opacity="0.72" />
                    <ellipse cx="70" cy="68" rx="26" ry="18" fill="white" opacity="0.82" />
                    <ellipse cx="112" cy="136" rx="32" ry="18" fill="white" opacity="0.65" />
                </svg>`
        };
        return switchCase[art] || switchCase['linen'];
    }

    FEATURED.forEach(j => {
        const container = document.getElementById(`svg-container-${j.id}`);
        if (container) container.innerHTML = generateSVG(j.art, j.bg);
        const band = document.getElementById(`band-${j.id}`);
        if (band) band.style.backgroundColor = j.elastic;
    });

    const oboModal = document.getElementById('obo-modal');
    const oboCloseBtn = document.getElementById('obo-close-btn');

    function getSceneSVG(idx) {
        var s = idx % 10;
        var scenes = [
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s0sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A3D28"/><stop offset="100%" stop-color="#4A7840"/></linearGradient><radialGradient id="s0sun" cx="52%" cy="32%" r="55%"><stop offset="0%" stop-color="#FFD080" stop-opacity="0.55"/><stop offset="100%" stop-color="transparent"/></radialGradient></defs><rect fill="url(#s0sky)" width="200" height="200"/><rect fill="url(#s0sun)" width="200" height="200"/><ellipse cx="55" cy="125" rx="32" ry="46" fill="#0E2A1A" opacity="0.92"/><ellipse cx="148" cy="115" rx="36" ry="55" fill="#0A2014" opacity="0.9"/><rect x="51" y="145" width="9" height="55" fill="#2A1A0C"/><rect x="144" y="148" width="9" height="52" fill="#2A1A0C"/><ellipse cx="100" cy="188" rx="85" ry="22" fill="#162E12"/><circle cx="100" cy="162" r="9" fill="#F5C89A"/><ellipse cx="100" cy="173" rx="12" ry="7" fill="#8A6850"/><ellipse cx="76" cy="181" rx="9" ry="5" fill="#C07040"/><ellipse cx="122" cy="183" rx="7" ry="4" fill="#D8D8C8"/><ellipse cx="132" cy="180" rx="5" ry="3" fill="#C0C0B0"/><line x1="100" y1="28" x2="65" y2="155" stroke="rgba(255,220,100,0.14)" stroke-width="20"/><line x1="100" y1="28" x2="135" y2="148" stroke="rgba(255,220,100,0.10)" stroke-width="15"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s1sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#0E1830"/><stop offset="60%" stop-color="#2A3870"/><stop offset="100%" stop-color="#5060A8"/></linearGradient><linearGradient id="s1sea" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A2858"/><stop offset="100%" stop-color="#0A1020"/></linearGradient></defs><rect fill="url(#s1sky)" width="200" height="200"/><ellipse cx="100" cy="95" rx="28" ry="28" fill="rgba(255,220,140,0.18)"/><ellipse cx="100" cy="95" rx="16" ry="16" fill="rgba(255,240,180,0.45)"/><rect fill="url(#s1sea)" x="0" y="110" width="200" height="90"/><path d="M0 120 Q50 112 100 120 Q150 128 200 120 L200 200 L0 200Z" fill="rgba(20,40,100,0.6)"/><path d="M0 135 Q40 130 80 135 Q120 140 160 135 Q180 132 200 135" stroke="rgba(100,150,255,0.25)" stroke-width="2" fill="none"/><path d="M20 150 Q60 145 100 150 Q140 155 180 150" stroke="rgba(100,150,255,0.15)" stroke-width="1.5" fill="none"/><circle cx="30" cy="65" r="1.5" fill="rgba(255,255,200,0.8)"/><circle cx="75" cy="40" r="1" fill="rgba(255,255,200,0.7)"/><circle cx="150" cy="55" r="1.5" fill="rgba(255,255,200,0.8)"/><circle cx="170" cy="30" r="1" fill="rgba(255,255,200,0.6)"/><circle cx="55" cy="25" r="1" fill="rgba(255,255,200,0.6)"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s2bg" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A2030"/><stop offset="100%" stop-color="#101520"/></linearGradient></defs><rect fill="url(#s2bg)" width="200" height="200"/><rect x="10" y="10" width="180" height="180" fill="rgba(60,100,140,0.12)" rx="6"/><line x1="100" y1="10" x2="100" y2="190" stroke="rgba(80,120,160,0.3)" stroke-width="3"/><line x1="10" y1="100" x2="190" y2="100" stroke="rgba(80,120,160,0.3)" stroke-width="3"/><g stroke="rgba(160,210,255,0.45)" stroke-width="1.2" stroke-linecap="round"><line x1="30" y1="5" x2="25" y2="30"/><line x1="55" y1="0" x2="50" y2="25"/><line x1="80" y1="8" x2="75" y2="33"/><line x1="120" y1="3" x2="115" y2="28"/><line x1="155" y1="0" x2="150" y2="25"/><line x1="178" y1="6" x2="173" y2="31"/><line x1="40" y1="40" x2="35" y2="65"/><line x1="70" y1="45" x2="65" y2="70"/><line x1="105" y1="38" x2="100" y2="63"/><line x1="140" y1="42" x2="135" y2="67"/><line x1="170" y1="40" x2="165" y2="65"/><line x1="20" y1="80" x2="15" y2="105"/><line x1="60" y1="85" x2="55" y2="110"/><line x1="95" y1="78" x2="90" y2="103"/><line x1="130" y1="82" x2="125" y2="107"/><line x1="165" y1="80" x2="160" y2="105"/><line x1="35" y1="120" x2="30" y2="145"/><line x1="75" y1="125" x2="70" y2="150"/><line x1="115" y1="118" x2="110" y2="143"/><line x1="150" y1="122" x2="145" y2="147"/><line x1="185" y1="120" x2="180" y2="145"/></g><circle cx="50" cy="30" r="2.5" fill="rgba(180,220,255,0.4)"/><circle cx="130" cy="65" r="2" fill="rgba(180,220,255,0.35)"/><circle cx="75" cy="110" r="3" fill="rgba(180,220,255,0.3)"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s3sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#080C20"/><stop offset="100%" stop-color="#1A1A3A"/></linearGradient></defs><rect fill="url(#s3sky)" width="200" height="200"/><polygon points="100,20 45,110 155,110" fill="#1A1A38"/><polygon points="100,20 45,110 155,110" fill="rgba(200,200,255,0.06)"/><polygon points="100,30 55,110 92,110" fill="#E8E8F5" opacity="0.85"/><polygon points="100,30 108,110 155,110" fill="#D0D0E8" opacity="0.7"/><polygon points="40,70 0,140 85,140" fill="#14142E"/><polygon points="40,70 10,140 55,140" fill="#E0E0F0" opacity="0.6"/><polygon points="160,60 115,140 200,140" fill="#14142E"/><polygon points="160,60 148,140 195,140" fill="#E0E0F0" opacity="0.55"/><rect x="0" y="140" width="200" height="60" fill="#0C0C1E"/><path d="M0 145 Q50 140 100 145 Q150 150 200 145 L200 200 L0 200Z" fill="#10101C"/><circle cx="35" cy="25" r="1.2" fill="rgba(255,255,200,0.9)"/><circle cx="80" cy="15" r="0.9" fill="rgba(255,255,200,0.8)"/><circle cx="165" cy="20" r="1.2" fill="rgba(255,255,200,0.9)"/><circle cx="140" cy="10" r="0.9" fill="rgba(255,255,200,0.8)"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s4sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A3020"/><stop offset="100%" stop-color="#2A4830"/></linearGradient></defs><rect fill="url(#s4sky)" width="200" height="200"/><ellipse cx="100" cy="110" rx="55" ry="16" fill="rgba(20,60,20,0.7)"/><path d="M85 200 L92 110 L108 110 L115 200Z" fill="#2A3818"/><path d="M88 200 L94 115 L106 115 L112 200Z" fill="#3A5025"/><ellipse cx="20" cy="150" rx="25" ry="35" fill="#0E2210"/><ellipse cx="25" cy="145" rx="20" ry="28" fill="#142E14"/><ellipse cx="180" cy="145" rx="25" ry="35" fill="#0E2210"/><ellipse cx="175" cy="140" rx="20" ry="28" fill="#142E14"/><circle cx="40" cy="130" r="8" fill="#1A3A10"/><circle cx="160" cy="125" r="8" fill="#1A3A10"/><circle cx="50" cy="160" r="5" fill="#FF6080" opacity="0.7"/><circle cx="42" cy="168" r="4" fill="#FF80A0" opacity="0.6"/><circle cx="152" cy="155" r="5" fill="#FF6080" opacity="0.7"/><rect x="0" y="170" width="200" height="30" fill="#1A2810"/><path d="M90 120 Q95 140 100 170 Q105 140 110 120" fill="#2A4018" opacity="0.5"/><circle cx="100" cy="60" r="20" fill="rgba(255,220,100,0.12)"/><circle cx="100" cy="60" r="10" fill="rgba(255,220,100,0.25)"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="s5bg" cx="50%" cy="50%" r="70%"><stop offset="0%" stop-color="#12183A"/><stop offset="100%" stop-color="#060810"/></radialGradient><radialGradient id="s5glow" cx="30%" cy="25%" r="40%"><stop offset="0%" stop-color="rgba(100,130,255,0.18)"/><stop offset="100%" stop-color="transparent"/></radialGradient></defs><rect fill="url(#s5bg)" width="200" height="200"/><rect fill="url(#s5glow)" width="200" height="200"/><g fill="rgba(255,255,220,1)"><circle cx="20" cy="18" r="1.3"/><circle cx="45" cy="8" r="1.8" opacity="0.9"/><circle cx="70" cy="22" r="1.1"/><circle cx="98" cy="12" r="1.5"/><circle cx="130" cy="5" r="1.2"/><circle cx="158" cy="18" r="1.8" opacity="0.9"/><circle cx="178" cy="9" r="1.1"/><circle cx="12" cy="45" r="1.2"/><circle cx="55" cy="38" r="1.5"/><circle cx="85" cy="50" r="1.1"/><circle cx="115" cy="35" r="1.3"/><circle cx="145" cy="42" r="1.6"/><circle cx="172" cy="32" r="1.2"/><circle cx="30" cy="70" r="1.4"/><circle cx="62" cy="62" r="1.1"/><circle cx="92" cy="75" r="1.5"/><circle cx="122" cy="60" r="1.2"/><circle cx="150" cy="68" r="1.4"/><circle cx="185" cy="55" r="1.1"/></g><path d="M100 30 L102 38 L110 38 L104 43 L106 51 L100 46 L94 51 L96 43 L90 38 L98 38Z" fill="rgba(255,240,160,0.55)" transform="scale(0.7) translate(43,30)"/><ellipse cx="100" cy="175" rx="80" ry="25" fill="#080C18"/><path d="M20 160 Q60 155 100 160 Q140 165 180 160" stroke="rgba(60,80,160,0.2)" stroke-width="1.5" fill="none"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s6sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A100C"/><stop offset="100%" stop-color="#2E1808"/></linearGradient></defs><rect fill="url(#s6sky)" width="200" height="200"/><rect x="0" y="165" width="200" height="35" fill="#1A0C08"/><rect x="90" y="100" width="8" height="65" fill="#2A1404"/><ellipse cx="94" cy="90" rx="42" ry="48" fill="#1A1008"/><ellipse cx="80" cy="80" rx="28" ry="32" fill="#1E1208"/><ellipse cx="108" cy="85" rx="24" ry="28" fill="#1A1008"/><g opacity="0.9"><ellipse cx="55" cy="60" rx="12" ry="8" fill="#C04010" transform="rotate(-30 55 60)"/><ellipse cx="145" cy="50" rx="10" ry="7" fill="#E05010" transform="rotate(20 145 50)"/><ellipse cx="35" cy="100" rx="9" ry="6" fill="#A03010" transform="rotate(-45 35 100)"/><ellipse cx="168" cy="85" rx="11" ry="7" fill="#D04810" transform="rotate(35 168 85)"/><ellipse cx="70" cy="145" rx="10" ry="7" fill="#B03808" transform="rotate(-20 70 145)"/><ellipse cx="130" cy="140" rx="9" ry="6" fill="#C04010" transform="rotate(15 130 140)"/><ellipse cx="100" cy="155" rx="8" ry="5" fill="#E06018" transform="rotate(-10 100 155)"/><ellipse cx="50" cy="170" rx="12" ry="8" fill="#A03010" transform="rotate(40 50 170)"/><ellipse cx="155" cy="165" rx="10" ry="7" fill="#D04818" transform="rotate(-25 155 165)"/></g></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s7sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1A1E30"/><stop offset="100%" stop-color="#2A3050"/></linearGradient></defs><rect fill="url(#s7sky)" width="200" height="200"/><ellipse cx="100" cy="92" rx="50" ry="50" fill="rgba(230,235,255,0.06)"/><rect x="0" y="130" width="200" height="70" fill="#1A2030"/><path d="M0 130 Q50 122 100 130 Q150 138 200 130 L200 200 L0 200Z" fill="#141820"/><path d="M0 142 Q40 136 80 142 Q120 148 160 142 Q180 139 200 142" stroke="rgba(200,215,255,0.2)" stroke-width="1.5" fill="none"/><g stroke="rgba(200,220,255,0.5)" stroke-linecap="round" stroke-width="1.2"><line x1="30" y1="90" x2="30" y2="100"/><line x1="25" y1="95" x2="35" y2="95"/><line x1="27" y1="91" x2="33" y2="99"/><line x1="33" y1="91" x2="27" y2="99"/><line x1="80" y1="55" x2="80" y2="65"/><line x1="75" y1="60" x2="85" y2="60"/><line x1="77" y1="56" x2="83" y2="64"/><line x1="83" y1="56" x2="77" y2="64"/><line x1="155" y1="80" x2="155" y2="90"/><line x1="150" y1="85" x2="160" y2="85"/><line x1="152" y1="81" x2="158" y2="89"/><line x1="158" y1="81" x2="152" y2="89"/></g><g fill="rgba(220,230,255,0.7)"><circle cx="25" cy="50" r="1.5"/><circle cx="60" cy="35" r="1.2"/><circle cx="110" cy="20" r="1.5"/><circle cx="165" cy="40" r="1.2"/><circle cx="185" cy="70" r="1"/></g><rect x="88" y="80" width="6" height="45" fill="#2A3848"/><ellipse cx="91" cy="76" rx="14" ry="18" fill="#1E2838"/></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s8sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1E1028"/><stop offset="100%" stop-color="#301828"/></linearGradient></defs><rect fill="url(#s8sky)" width="200" height="200"/><rect x="0" y="160" width="200" height="40" fill="#180C18"/><rect x="95" y="120" width="7" height="40" fill="#1C1014"/><path d="M98 120 Q70 100 50 70 Q80 80 98 120Z" fill="#1C1014"/><path d="M98 120 Q130 95 155 65 Q125 80 98 120Z" fill="#1C1014"/><path d="M98 120 Q75 85 85 45 Q100 75 98 120Z" fill="#1C1014"/><g opacity="0.85"><circle cx="60" cy="75" r="5" fill="#E8609A"/><circle cx="58" cy="80" r="4.5" fill="#F080B0"/><circle cx="55" cy="72" r="3.5" fill="#E060A0"/><circle cx="65" cy="78" r="4" fill="#F088B8"/><circle cx="85" cy="55" r="5" fill="#E8609A"/><circle cx="83" cy="60" r="4.5" fill="#F080B0"/><circle cx="90" cy="52" r="3.5" fill="#E060A0"/><circle cx="78" cy="58" r="4" fill="#F088B8"/><circle cx="140" cy="68" r="5" fill="#E8609A"/><circle cx="138" cy="73" r="4.5" fill="#F080B0"/><circle cx="145" cy="65" r="3.5" fill="#E060A0"/><circle cx="133" cy="70" r="4" fill="#F088B8"/><circle cx="108" cy="48" r="5" fill="#E8609A"/><circle cx="106" cy="53" r="4.5" fill="#F080B0"/></g><g fill="rgba(240,160,200,0.6)" font-size="6"><text x="30" y="120">❋</text><text x="155" y="130">❋</text><text x="68" y="150">❋</text><text x="120" y="158">❋</text><text x="45" y="165">❋</text><text x="170" y="155">❋</text></g></svg>',
            '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="s9sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#080E18"/><stop offset="100%" stop-color="#141C30"/></linearGradient><linearGradient id="s9water" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#0C1828"/><stop offset="100%" stop-color="#060E14"/></linearGradient></defs><rect fill="url(#s9sky)" width="200" height="100"/><rect fill="url(#s9water)" x="0" y="100" width="200" height="100"/><path d="M0 100 Q30 95 60 100 Q90 105 120 100 Q150 95 180 100 Q190 101 200 100" stroke="rgba(80,140,180,0.18)" stroke-width="1" fill="none"/><rect x="0" y="98" width="200" height="4" fill="rgba(40,80,120,0.3)"/><ellipse cx="60" cy="70" rx="22" ry="28" fill="#0A1820"/><ellipse cx="140" cy="65" rx="28" ry="34" fill="#0A1820"/><rect x="56" y="90" width="7" height="10" fill="#0A1018"/><rect x="136" y="90" width="7" height="10" fill="#0A1018"/><path d="M60 105 Q62 112 60 118 Q58 125 60 130 Q62 138 60 145" stroke="rgba(80,140,180,0.3)" stroke-width="18" stroke-linecap="round" fill="none"/><path d="M140 105 Q138 112 140 118 Q142 125 140 130 Q138 138 140 145" stroke="rgba(80,140,180,0.3)" stroke-width="22" stroke-linecap="round" fill="none"/><circle cx="100" cy="30" r="14" fill="rgba(255,220,120,0.18)"/><circle cx="100" cy="30" r="7" fill="rgba(255,220,120,0.4)"/><path d="M90 170 Q100 165 110 170 Q100 175 90 170Z" fill="rgba(255,220,120,0.35)"/><path d="M88 160 Q100 155 112 160" stroke="rgba(255,220,100,0.2)" stroke-width="2" fill="none"/></svg>'
        ];
        return scenes[s];
    }

    function getDeterministicLetter(entry) {
        let text = entry.content || "";
        if (text.trim().startsWith('{') && text.trim().endsWith('}')) {
            try {
                const data = JSON.parse(text);
                text = data.text || text;
            } catch (e) {}
        }
        let charSum = 0;
        for (let i = 0; i < text.length; i++) {
            charSum += text.charCodeAt(i);
        }
        const index = charSum % 3;
        const score = entry.mood_score || 5;
        const username = window.currentUsername || 'friend';
        const name = username.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

        if (score >= 7) {
            const options = [
                `Dear ${name},\n\nSomething in the way you wrote today felt lighter — more alive. Like you were writing from a place of genuine warmth.\n\nWhatever is filling your days with that feeling, hold onto it gently. Not too tightly, just enough to remember it's there.\n\nI'm glad today was a good one.`,
                `Dear ${name},\n\nToday's words carry a brightness to them. There's something lovely about a day that leaves you with something worth writing down.\n\nKeep going. You're doing beautifully.`,
                `Dear ${name},\n\nYou wrote today with something that sounded a lot like joy — or maybe just ease. Either way, it looked good on you.\n\nSee you on the next page.`
            ];
            return options[index];
        } else if (score === 1 || score === 2 || score === 3 || score === 4) {
            const options = [
                `Dear ${name},\n\nHard days have a weight that's difficult to put into words — and yet here you are, doing just that.\n\nThat takes more courage than you might realize. Writing through the difficult moments is its own kind of bravery.\n\nTomorrow is a fresh page.`,
                `Dear ${name},\n\nIt sounds like today asked a lot of you. I hope you're being as gentle with yourself as you deserve.\n\nSome days we write to feel better. Some days we write just to survive them. Both are enough.`,
                `Dear ${name},\n\nNot every day is easy, and this one doesn't seem to have been. But you're still here, still writing.\n\nThat matters more than you know. Rest well tonight.`
            ];
            return options[index];
        } else {
            const options = [
                `Dear ${name},\n\nNot every day needs to be extraordinary. Some days are simply lived — and those quiet, steady days are worth remembering too.\n\nThank you for showing up and writing anyway. That says something good about you.`,
                `Dear ${name},\n\nThere's something peaceful about a day in the middle. Not too high, not too low — just present.\n\nYou took a moment to reflect, and that's never wasted. See you on the next page.`,
                `Dear ${name},\n\nToday was a day. And you wrote about it. That's more than most people do.\n\nSee you tomorrow.`
            ];
            return options[index];
        }
    }

    function openOverlay(title, pages, entry = null) {
        document.getElementById('obo-dyn-title').textContent = title;
        document.getElementById('obo-dyn-pages').textContent = pages;

        const leftBox = document.querySelector('.obo-left');
        const rightBox = document.querySelector('.obo-right');

        if (entry) {
            let contentText = "No thoughts recorded for this day.";
            try {
                const parsed = JSON.parse(entry.content);
                contentText = parsed.text || contentText;
            } catch (e) {
                contentText = entry.content || contentText;
            }

            leftBox.innerHTML = `
                <div style="padding: 10px; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; box-sizing: border-box; background: #EDE4D2; width: 100%;">
                    <div style="position: relative; width: 280px; height: 380px; display: flex; justify-content: center; align-items: flex-end;">
                        <!-- 1. Envelope Back & Open Flap -->
                        <svg width="270" height="230" viewBox="0 0 270 230" style="position: absolute; bottom: 0; left: 5px; z-index: 1;">
                            <!-- Envelope Back Rect -->
                            <rect x="0" y="120" width="270" height="110" fill="#C2B29F" rx="4" />
                            <!-- Inner shadow of the pocket (top area) -->
                            <rect x="10" y="120" width="250" height="15" fill="#A59582" opacity="0.4" />
                            <!-- Opened back flap pointing upwards -->
                            <path d="M 0,120 L 135,20 L 270,120 Z" fill="#D0C0AF" />
                            <path d="M 0,120 L 135,20 L 270,120" stroke="#B3A392" stroke-width="1.5" fill="none" />
                        </svg>

                        <!-- 2. The Letter (Sticking out) -->
                        <div class="letter-sheet" style="position: absolute; bottom: 54px; left: 17px; width: 246px; height: 290px; background: #FAF7F0; border-radius: 4px; box-shadow: 0 6px 18px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05); z-index: 2; display: flex; flex-direction: column; padding: 22px 20px 42px 20px; box-sizing: border-box; transform: rotate(-1deg); border: 1px solid #ECE7DC;">
                            <!-- Letter content -->
                            <div style="flex-grow: 1; overflow-y: auto; font-family: 'Lora', serif; font-size: 12.5px; line-height: 1.65; color: #4A4438; padding-right: 4px; scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.06) transparent;">
                                <p style="white-space: pre-wrap; margin: 0; font-style: italic; text-align: left; letter-spacing: 0.01em;">
                                    ${getDeterministicLetter(entry)}
                                </p>
                            </div>
                            <!-- Letter signature/footer -->
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px; border-top: 1px dashed rgba(75, 46, 31, 0.15); padding-top: 8px;">
                                <span style="font-family: 'Lora', serif; font-size: 11px; color: #8C8476; font-style: italic; letter-spacing: 0.05em;">— MoodBlume ✿</span>
                                <div style="width: 14px; height: 14px; border-radius: 50%; background: #a84239; box-shadow: 0 1px 3px rgba(0,0,0,0.15); opacity: 0.8;"></div>
                            </div>
                        </div>

                        <!-- 3. Envelope Front Pocket -->
                        <svg width="270" height="150" viewBox="0 0 270 150" style="position: absolute; bottom: 0; left: 5px; z-index: 3; filter: drop-shadow(0 -3px 5px rgba(0,0,0,0.08)) drop-shadow(0 4px 10px rgba(0,0,0,0.12));">
                            <!-- Left side flap -->
                            <path d="M 0,40 L 135,95 L 0,150 Z" fill="#CBBBA9" />
                            <!-- Right side flap -->
                            <path d="M 270,40 L 135,95 L 270,150 Z" fill="#CBBBA9" />
                            <!-- Bottom flap -->
                            <path d="M 0,150 L 135,90 L 270,150 Z" fill="#BDAD9A" />
                            <!-- Realistic shadows/lines -->
                            <path d="M 0,40 L 135,95" stroke="#E5D8C8" stroke-width="1.5" opacity="0.6" />
                            <path d="M 270,40 L 135,95" stroke="#E5D8C8" stroke-width="1.5" opacity="0.6" />
                            <path d="M 0,150 L 135,90 L 270,150" stroke="#A29280" stroke-width="1" fill="none" />
                        </svg>
                    </div>
                </div>
            `;

            rightBox.innerHTML = `
                <div style="padding: 45px; height: 100%; font-family: 'Lora', serif; font-size: 16px; line-height: 1.9; color: #4A4438; position: relative; overflow: hidden;">
                    <div class="obo-lines" style="opacity: 0.35; pointer-events: none;"></div>
                    <div style="position: relative; z-index: 2; height: 100%; overflow-y: auto; padding-right: 15px; scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.1) transparent;">
                        ${contentText}
                    </div>
                </div>
            `;
        } else {
            
            leftBox.innerHTML = `
                <span class="obo-left-text">EX LIBRIS</span>
                <div class="obo-left-hr"></div>
            `;
            rightBox.innerHTML = `<div class="obo-lines"></div><p id="obo-dyn-writ" style="position:relative; z-index:2; margin: 40px; color: #8C8476; font-style: italic;">Select an entry to view details...</p>`;
        }

        oboModal.classList.add('visible');
    }

    window.openEntryFromCalendar = function (id) {
        const entry = ENTRIES_DATA.find(e => e.id == id);
        if (entry) {
            const date = new Date(entry.iso_date);
            const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            const title = `${months[date.getMonth()]} ${date.getDate()}`;
            openOverlay(title, entry.theme || "Personal Chronicle", entry);
        }
    };

    function closeOverlay() {
        oboModal.classList.remove('visible');
    }

    oboCloseBtn.addEventListener('click', closeOverlay);
    oboModal.addEventListener('click', (e) => {
        if (e.target === oboModal) closeOverlay();
    });
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeOverlay();
    });

    const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    const NOW = new Date();
    const TODAY_Y = NOW.getFullYear();
    const TODAY_M = NOW.getMonth();
    const TODAY_D = NOW.getDate();

    let curYear = TODAY_Y;
    let curMonth = TODAY_M;

    const entriesByDate = {};
    ENTRIES_DATA.forEach(e => {
        if (e.iso_date) entriesByDate[e.iso_date] = e;
    });

    function getEntryForDay(y, m, d) {
        const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        return entriesByDate[dateStr];
    }

    const EMOTIONS = ['e-joy', 'e-sadness', 'e-anger', 'e-fear', 'e-disgust', 'e-confuse'];

    function hash(y, m, d) {
        let s = y * 10000 + m * 100 + d;
        s = ((s ^ (s >> 4)) * 0x45d9f3b) & 0xffffffff;
        s = ((s ^ (s >> 15)) * 0x45d9f3b) & 0xffffffff;
        s ^= s >> 4;
        return Math.abs(s);
    }

    function emotionClassForEntry(entry, y, m, d) {
        if (entry) {
            const score = entry.mood_score;
            if (score >= 7) return 'e-joy';
            if (score === 6) return 'e-disgust';
            if (score === 5) return 'e-none';
            if (score === 4) return 'e-confuse';
            if (score === 3) return 'e-fear';
            if (score === 2) return 'e-sadness';
            if (score === 1) return 'e-anger';
        }
        
        return 'e-none';
    }

    function isFuture(y, m, d) {
        if (y > TODAY_Y) return true;
        if (y === TODAY_Y && m > TODAY_M) return true;
        if (y === TODAY_Y && m === TODAY_M && d > TODAY_D) return true;
        return false;
    }

    function renderCalendar() {
        const monthLabel = document.getElementById('monthLabel');
        const yearLabel = document.getElementById('yearLabel');
        if (monthLabel) monthLabel.textContent = MONTHS[curMonth];
        if (yearLabel) yearLabel.textContent = curYear;

        const grid = document.getElementById('calGrid');
        if (!grid) return;
        grid.innerHTML = '';

        ['M','T','W','T','F','S','S'].forEach(d => {
            const el = document.createElement('div');
            el.className = 'cal-dow';
            el.textContent = d;
            grid.appendChild(el);
        });

        const firstDay = new Date(curYear, curMonth, 1).getDay();
        const offset = firstDay === 0 ? 6 : firstDay - 1;
        const daysInMonth = new Date(curYear, curMonth + 1, 0).getDate();

        for (let i = 0; i < offset; i++) {
            const el = document.createElement('div');
            el.className = 'cal-day'; 
            grid.appendChild(el);
        }

        for (let d = 1; d <= daysInMonth; d++) {
            const el = document.createElement('div');
            const future = isFuture(curYear, curMonth, d);
            const entry = getEntryForDay(curYear, curMonth, d);

            el.className = 'cal-day';
            if (future) {
                el.classList.add('e-future');
                el.innerHTML = `<span class="cal-day-num">${d}</span>`;
            } else {
                const emoClass = emotionClassForEntry(entry, curYear, curMonth, d);
                el.classList.add(emoClass);
                if (emoClass !== 'e-none') {
                    let mouthStyle = 'm-smile';
                    if (emoClass === 'e-sadness' || emoClass === 'e-anger' || emoClass === 'e-fear') {
                        mouthStyle = 'm-frown';
                    } else if (emoClass === 'e-confuse') {
                        mouthStyle = 'm-flat';
                    }
                    el.innerHTML = `
                        <span class="cal-day-num">${d}</span>
                        <div class="mini-blob-face">
                            <div class="mini-blob-eyes">
                                <span class="mini-blob-eye"></span>
                                <span class="mini-blob-eye"></span>
                            </div>
                            <span class="mini-blob-mouth ${mouthStyle}"></span>
                        </div>
                    `;
                } else {
                    el.innerHTML = `<span class="cal-day-num">${d}</span>`;
                }
            }

            if (d === TODAY_D && curMonth === TODAY_M && curYear === TODAY_Y) {
                el.classList.add('today-ring');
            }

            if (entry) {
                el.setAttribute('title', `${entry.mood_label} · Click to read`);
                el.addEventListener('click', () => {
                    openEntryFromCalendar(entry.id);
                });
            } else if (!future) {
                el.setAttribute('title', `No entry · Click to write`);
                el.addEventListener('click', () => {
                    window.location.href = '/writing';
                });
            }

            grid.appendChild(el);
        }
    }

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const todayBtn = document.getElementById('todayBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            curMonth--; 
            if (curMonth < 0) { curMonth = 11; curYear--; } 
            renderCalendar();
        });
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            curMonth++; 
            if (curMonth > 11) { curMonth = 0; curYear++; } 
            renderCalendar();
        });
    }
    if (todayBtn) {
        todayBtn.addEventListener('click', () => {
            curYear = TODAY_Y; 
            curMonth = TODAY_M; 
            renderCalendar();
        });
    }

    renderCalendar();

    let libGrid, btnNewVol;

    function cardHTML(e, idx) {
        return `
        <div class="lib-journal-item" data-id="${e.id}" style="cursor: pointer;">
            <div class="premium-book" id="lib-book-${e.id}">
                <div class="book-pages"></div>
                <div class="book-cover">
                    <div class="cover-front">
                        <div class="cover-label">
                            <span class="lbl-small">a memory from</span>
                            <span class="lbl-big">${e.formatted_date}</span>
                        </div>
                    </div>
                    <div class="cover-back">
                        <span style="font-family:'Lora',serif; font-size:10px; color:#B0A090; letter-spacing:0.2em; text-transform:uppercase;">Ex Libris</span>
                    </div>
                    <div class="elastic-band"></div>
                </div>
            </div>
            <div class="flat-meta"><h3>${e.formatted_date}</h3></div>
        </div>`;
    }

    function groupHTML(label, entries) {
        if (!entries.length) return '';
        return `<div class="shelf-row">
            <div class="shelf-header">
                <span class="shelf-label">${label}</span>
                <span class="shelf-count">${entries.length} ${entries.length === 1 ? 'entry' : 'entries'}</span>
            </div>
            <div class="shelf-books">${entries.map((e, idx) => cardHTML(e, idx)).join('')}</div>
        </div>`;
    }

    function dominantClass(entries) {
        const freq = {};
        entries.forEach(e => { freq[e.color_class] = (freq[e.color_class] || 0) + 1; });
        return Object.keys(freq).sort((a, b) => freq[b] - freq[a])[0] || 'c-ochre';
    }

    function renderMonthDrilldown(monthLabel) {
        const entries = ENTRIES_DATA.filter(e => e.month_label === monthLabel);
        libGrid.innerHTML = `
            <div class="lib-breadcrumb">
                <button onclick="renderView('monthly')">&#8592; All Months</button>
                <span>/</span>
                <span style="color:var(--text)">${monthLabel}</span>
            </div>
            <div class="shelf-books">${entries.map(cardHTML).join('')}</div>
        `;
    }

    function renderView(mode) {
        btnNewVol.classList.toggle('visible', mode === 'volumes');
        let html = '';

        if (mode === 'all') {
            const cards = ENTRIES_DATA.map((e, idx) => cardHTML(e, idx)).join('');
            html = ENTRIES_DATA.length
                ? `<div class="shelf-books" style="margin-top:0">${cards}</div>`
                : `<div class="lib-empty">No entries yet — start writing in the Sanctuary.</div>`;

        } else if (mode === 'monthly') {
            
            const groups = {};
            ENTRIES_DATA.forEach(e => { (groups[e.month_label] = groups[e.month_label] || []).push(e); });
            const monthCards = Object.keys(groups).map((month, idx) => {
                const entries = groups[month];
                const [mon, yr] = month.split(' ');

                return `
                <div class="lib-journal-item" data-month="${month}" style="cursor: pointer;">
                    <div class="premium-book">
                        <div class="book-pages"></div>
                        <div class="book-cover">
                            <div class="cover-front">
                                <div class="cover-label">
                                    <span class="lbl-small">memories from</span>
                                    <span class="lbl-big">${mon}<br><span style="font-size:9px; opacity:0.6; font-weight:normal;">${yr}</span></span>
                                </div>
                            </div>
                            <div class="cover-back"></div>
                            <div class="elastic-band"></div>
                        </div>
                    </div>
                    <div class="flat-meta">
                        <h3>${month}</h3>
                        <p style="font-size:10px; color:var(--muted); margin-top:2px;">${entries.length} memories</p>
                    </div>
                </div>`;
            }).join('');
            html = monthCards
                ? `<div class="shelf-books" style="margin-top:0">${monthCards}</div>`
                : `<div class="lib-empty">No entries yet.</div>`;

        } else if (mode === 'mood') {
            const ORDER = ['Happy', 'Calm', 'Neutral', 'Sad', 'Stressed'];
            const groups = {};
            ENTRIES_DATA.forEach(e => { (groups[e.mood_label] = groups[e.mood_label] || []).push(e); });
            html = ORDER.filter(o => groups[o]).map(o => groupHTML(o, groups[o])).join('') ||
                `<div class="lib-empty">No entries yet.</div>`;

        } else if (mode === 'volumes') {
            if (!COLLECTIONS.length) {
                html = `<div class="lib-empty">No collection volumes found.</div>`;
            } else {
                COLLECTIONS.forEach(col => {
                    const entries = ENTRIES_DATA.filter(e => e.collection_id === col.id);
                    html += groupHTML(col.name, entries);
                });
                const uncollected = ENTRIES_DATA.filter(e => !e.collection_id);
                if (uncollected.length) html += groupHTML('Uncollected', uncollected);
                if (!html) html = `<div class="lib-empty">Assign entries to a volume to see them here.</div>`;
            }
        }

        if (!html) {
            html = `<div class="lib-empty">No journals found in this collection.</div>`;
        }

        const grid = document.getElementById('library-grid');
        if (grid) {
            grid.innerHTML = html;
        } else {
            console.error("Library grid element not found");
        }
    }

    let activeView = 'monthly';
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeView = tab.dataset.view;
            renderView(activeView);
        });
    });
    
    window.addEventListener('load', () => {
        libGrid = document.getElementById('library-grid');
        btnNewVol = document.getElementById('btn-new-vol');
        const modeGridBtn = document.getElementById('mode-grid');
        const modeCarouselBtn = document.getElementById('mode-carousel');
        const libSection = document.querySelector('.library-section');

        if (modeGridBtn && modeCarouselBtn) {
            modeGridBtn.addEventListener('click', () => {
                modeGridBtn.classList.add('active');
                modeCarouselBtn.classList.remove('active');
                libSection.classList.remove('mode-carousel');
                renderView(activeView);
            });

            modeCarouselBtn.addEventListener('click', () => {
                modeCarouselBtn.classList.add('active');
                modeGridBtn.classList.remove('active');
                libSection.classList.add('mode-carousel');
                renderView(activeView);
                setTimeout(updateCarouselAnims, 50); 
            });
        }

        if (libSection.classList.contains('mode-carousel')) {
            modeCarouselBtn?.classList.add('active');
            modeGridBtn?.classList.remove('active');
            setTimeout(updateCarouselAnims, 100);
        } else {
            modeGridBtn?.classList.add('active');
            modeCarouselBtn?.classList.remove('active');
        }

        renderView('monthly');
    });

    function updateCarouselAnims() {
        const shelves = document.querySelectorAll('.library-section.mode-carousel .shelf-books');
        shelves.forEach(shelf => {
            const items = shelf.children;
            const shelfRect = shelf.getBoundingClientRect();
            const centerX = shelfRect.left + shelfRect.width / 2;

            Array.from(items).forEach(item => {
                const rect = item.getBoundingClientRect();
                const itemCenter = rect.left + rect.width / 2;
                const dist = Math.abs(centerX - itemCenter);
                const maxDist = shelfRect.width / 1.5;

                const normDist = Math.min(dist / maxDist, 1);
                const scale = 1.15 - (normDist * 0.45);
                const opacity = 1 - (normDist * 0.4);
                const translateY = (1 - normDist) * -15;

                item.style.transform = `scale(${scale}) translateY(${translateY}px)`;
                item.style.opacity = opacity;
                item.style.zIndex = Math.round((1 - normDist) * 100);
            });
        });
    }

    document.addEventListener('scroll', (e) => {
        if (e.target.classList?.contains('shelf-books')) {
            updateCarouselAnims();
        }
    }, true);

    document.addEventListener('click', (e) => {
        const libItem = e.target.closest('.lib-journal-item');
        if (!libItem) return;

        const libSection = document.querySelector('.library-section');
        const entryId = libItem.dataset.id;
        const monthLabel = libItem.dataset.month;

        const performAction = () => {
            if (monthLabel) renderMonthDrilldown(monthLabel);
            else if (entryId) openEntryFromCalendar(entryId);
        };

        if (!libSection?.classList.contains('mode-carousel')) {
            performAction();
            return;
        }

        const shelf = libItem.parentElement;
        if (!shelf) return;

        const shelfRect = shelf.getBoundingClientRect();
        const centerX = shelfRect.left + shelfRect.width / 2;
        const itemRect = libItem.getBoundingClientRect();
        const itemCenterX = itemRect.left + itemRect.width / 2;

        const distFromCenter = Math.abs(centerX - itemCenterX);

        if (distFromCenter < 80) {
            performAction();
        } else {
            libItem.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    });

    const colModalBg = document.getElementById('col-modal-bg');
    const colNameInput = document.getElementById('col-name-input');
    let selectedColor = '#C8D898';

    let isOpen3D = false;
    let isAnimating3D = false;
    const journal3d = document.getElementById('journal3d');
    const leftHalf3d = document.getElementById('leftHalf');
    const rightWing3d = document.getElementById('rightWing');
    const btnToggle3d = document.getElementById('btn-journal-toggle');
    const pickerWrap3d = document.getElementById('pickerWrap3D');
    const allPages = document.querySelectorAll('.journal-spotlight .page');

    const OPEN_DUR = 1200;
    const EASE = 'cubic-bezier(0.645, 0.045, 0.355, 1.000)';

    window.toggleJournal3D = function () {
        if (isAnimating3D) return;
        isAnimating3D = true;
        isOpen3D = !isOpen3D;

        if (isOpen3D) {
            journal3d.classList.add('spread-open');
            leftHalf3d.classList.add('wing-open');
            rightWing3d.classList.add('wing-open');
            if (btnToggle3d) btnToggle3d.textContent = 'Close Journal';
            setTimeout(() => { isAnimating3D = false; pickerWrap3d.classList.add('visible'); }, OPEN_DUR);
        } else {
            pickerWrap3d.classList.remove('visible');

            let delay = 0;
            const flippedPages = Array.from(allPages).filter(p => p.classList.contains('flipped')).reverse();

            flippedPages.forEach((p, i) => {
                setTimeout(() => p.classList.remove('flipped'), i * 150);
                delay = Math.max(delay, (i * 150) + 600);
            });

            setTimeout(() => {
                leftHalf3d.classList.remove('wing-open');
                rightWing3d.classList.remove('wing-open');
                setTimeout(() => {
                    journal3d.classList.remove('spread-open');
                    if (btnToggle3d) btnToggle3d.textContent = 'Open Journal';
                    isAnimating3D = false;
                    updateZIndices();
                }, 800);
            }, delay);
        }
    };

    function updateZIndices() {
        const flipped = Array.from(allPages).filter(p => p.classList.contains('flipped'));
        const lastFlipped = flipped[flipped.length - 1];
        const nextToFlip = Array.from(allPages).find(p => !p.classList.contains('flipped'));

        allPages.forEach((page, index) => {
            const isFlipped = page.classList.contains('flipped');
            page.style.zIndex = isFlipped ? 10 + index : 10 - index;
            if (page === lastFlipped || page === nextToFlip) {
                page.classList.add('active-page');
            } else {
                page.classList.remove('active-page');
            }
        });
    }

    window.addEventListener('load', () => {
        libGrid = document.getElementById('library-grid');
        const btnNewVol = document.getElementById('btn-new-vol');
        const modeGridBtn = document.getElementById('mode-grid');
        const modeCarouselBtn = document.getElementById('mode-carousel');
        const libSection = document.querySelector('.library-section');

        renderView('monthly');

        if (btnNewVol) {
            btnNewVol.addEventListener('click', () => {
                colNameInput.value = '';
                colModalBg.classList.add('visible');
                setTimeout(() => colNameInput.focus(), 300);
            });
        }
        document.getElementById('col-cancel-btn')?.addEventListener('click', () => colModalBg.classList.remove('visible'));
        colModalBg?.addEventListener('click', e => { if (e.target === colModalBg) colModalBg.classList.remove('visible'); });

        document.querySelectorAll('.col-swatch').forEach(sw => {
            sw.addEventListener('click', () => {
                document.querySelectorAll('.col-swatch').forEach(s => s.classList.remove('active'));
                sw.classList.add('active');
                selectedColor = sw.dataset.color;
            });
        });

        document.getElementById('col-create-btn')?.addEventListener('click', async () => {
            const name = colNameInput.value.trim();
            if (!name) { colNameInput.focus(); return; }
            const res = await fetch('/collections', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, cover_color: selectedColor, art_style: 'linen' })
            });
            const data = await res.json();
            if (data.success) {
                colModalBg.classList.remove('visible');
                COLLECTIONS.unshift({ id: data.id, name: data.name, cover_color: data.cover_color });
                if (activeView === 'volumes') renderView('volumes');
            }
        });

        if (modeGridBtn && modeCarouselBtn) {
            modeGridBtn.addEventListener('click', () => {
                modeGridBtn.classList.add('active');
                modeCarouselBtn.classList.remove('active');
                libSection.classList.remove('mode-carousel');
                renderView(activeView);
            });
            modeCarouselBtn.addEventListener('click', () => {
                modeCarouselBtn.classList.add('active');
                modeGridBtn.classList.remove('active');
                libSection.classList.add('mode-carousel');
                renderView(activeView);
            });
        }

        updateZIndices();
        allPages.forEach((page) => {
            
            page.addEventListener('click', (e) => { e.stopPropagation(); });
        });

        journal3d?.addEventListener('click', (e) => {
            if (!isOpen3D && !isAnimating3D) toggleJournal3D();
        });

        document.addEventListener('click', (e) => {
            if (isOpen3D && !isAnimating3D) {
                const isCoverInside = e.target.closest('.cover-inside');
                const isWing = e.target.closest('.wing');
                const isScene = e.target.closest('.scene');
                const isPage = e.target.closest('.page');
                const isControls = e.target.closest('.journal-controls');
                const isWritingArea = e.target.closest('.page-writing-area');
                if ((isCoverInside || isWing || isScene) && !isPage && !isControls && !isWritingArea) {
                    toggleJournal3D();
                }
            }
        });

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (isOpen3D && !isAnimating3D) toggleJournal3D();
                colModalBg?.classList.remove('visible');
            }
        });
    });

    window.setStyle3D = function (style) {
        const allPotential = document.querySelectorAll('.journal-spotlight .page, .journal-spotlight .page-front, .journal-spotlight .page-back, .journal-spotlight .wing, .journal-spotlight .cover-inside');
        allPotential.forEach(el => el.classList.remove('style-grid', 'style-blank', 'style-lined'));
        const faces = document.querySelectorAll('.journal-spotlight .page-front, .journal-spotlight .page-back');
        faces.forEach(el => el.classList.add('style-' + style));
    };

    (function initWritingAreas() {
        function addWritingArea(el, id, placeholderText, isBack) {
            const ph = document.createElement('div');
            ph.className = 'page-writing-placeholder';
            ph.textContent = placeholderText;
            ph.style.left = isBack ? '22px' : '38px';

            const area = document.createElement('div');
            area.className = 'page-writing-area';
            area.contentEditable = 'true';
            area.spellcheck = false;
            area.dataset.pageId = id;

            const saved = localStorage.getItem('journal-page-' + id);
            if (saved) area.innerHTML = saved;

            const isEmpty = () => area.textContent.trim() === '';
            const syncPh = () => { ph.style.display = isEmpty() ? '' : 'none'; };
            area.addEventListener('input', () => {
                syncPh();
                localStorage.setItem('journal-page-' + id, area.innerHTML);
            });
            syncPh();

            el.appendChild(ph);
            el.appendChild(area);
            return { area, ph, isEmpty };
        }

        document.querySelectorAll('.journal-spotlight .page').forEach((page, i) => {
            const pageNum = i + 1;
            const front = page.querySelector('.page-front');
            const back  = page.querySelector('.page-back');

            const { area: frontArea, ph: frontPh, isEmpty: frontEmpty } = addWritingArea(
                front, 'p' + pageNum + '-front',
                pageNum === 1 ? 'begin here...' : 'write freely...', false);
            const { area: backArea, ph: backPh, isEmpty: backEmpty } = addWritingArea(
                back, 'p' + pageNum + '-back', 'write freely...', true);

            const initFlipped = page.classList.contains('flipped');
            front.style.pointerEvents = initFlipped ? 'none' : 'auto';
            back.style.pointerEvents  = initFlipped ? 'auto' : 'none';

            backArea.style.display = 'none';
            backPh.style.display   = 'none';

            new MutationObserver(() => {
                const flipped = page.classList.contains('flipped');
                front.style.pointerEvents = flipped ? 'none' : 'auto';
                back.style.pointerEvents  = flipped ? 'auto' : 'none';

                frontArea.style.display = flipped ? 'none' : '';
                frontPh.style.display   = flipped ? 'none' : (frontEmpty() ? '' : 'none');
                backArea.style.display  = flipped ? ''     : 'none';
                
                backPh.style.display    = flipped ? (backEmpty() ? '' : 'none') : 'none';
            }).observe(page, { attributes: true, attributeFilter: ['class'] });

            const frontStrip = document.createElement('div');
            frontStrip.className = 'page-flip-strip';
            frontStrip.style.right = '0';
            front.appendChild(frontStrip);

            const backStrip = document.createElement('div');
            backStrip.className = 'page-flip-strip';
            backStrip.style.left = '0';  
            back.appendChild(backStrip);

            frontStrip.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!isOpen3D || isAnimating3D) return;
                if (!page.classList.contains('flipped')) {
                    const nextToFlip = Array.from(allPages).find(p => !p.classList.contains('flipped'));
                    if (page === nextToFlip) {
                        page.classList.add('flipped');
                        updateZIndices();
                    }
                }
            });

            backStrip.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!isOpen3D || isAnimating3D) return;
                if (page.classList.contains('flipped')) {
                    const flipped = Array.from(allPages).filter(p => p.classList.contains('flipped'));
                    if (page === flipped[flipped.length - 1]) {
                        page.classList.remove('flipped');
                        updateZIndices();
                    }
                }
            });
        });
    })();
