import os

svg_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
 "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="1200" height="800" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
    <style>
        .node { font-family: Arial, sans-serif; font-size: 12px; }
        .title { font-family: Arial, sans-serif; font-weight: bold; font-size: 16px; fill: #333; }
        .edge { stroke: #555555; stroke-width: 1.5; fill: none; marker-end: url(#arrow); }
        .doc-box { fill: #E3F2FD; stroke: #90CAF9; stroke-width: 2; rx: 8; ry: 8; }
        .apostille-box { fill: #FFFDE7; stroke: #FFF59D; stroke-width: 2; rx: 8; ry: 8; }
        .sig-box { fill: #E8F5E9; stroke: #A5D6A7; stroke-width: 2; rx: 8; ry: 8; }
        .status-box { fill: #F3E5F5; stroke: #CE93D8; stroke-width: 2; rx: 8; ry: 8; }
        .text-bold { font-weight: bold; fill: #111; }
        .text-sm { font-size: 10px; fill: #555; }
        .label-text { font-size: 10px; fill: #444; background: #fff; }
    </style>
    
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 2 L 10 5 L 0 8 z" fill="#555555"/>
        </marker>
    </defs>

    <!-- Background -->
    <rect width="100%" height="100%" fill="#FAFAFA"/>
    
    <!-- Title -->
    <text x="50" y="40" class="title">ACTOR MASTER EVIDENCE GRAPH — Signature &amp; Apostille Audit (Jus Cogens)</text>

    <!-- Legend -->
    <g transform="translate(50, 60)">
        <rect x="0" y="0" width="1100" height="40" fill="#FFFFFF" stroke="#CCCCCC" rx="4" ry="4"/>
        <rect x="20" y="12" width="15" height="15" fill="#E3F2FD" stroke="#90CAF9"/>
        <text x="40" y="24" class="node">Исходный документ</text>
        
        <rect x="180" y="12" width="15" height="15" fill="#FFFDE7" stroke="#FFF59D"/>
        <text x="200" y="24" class="node">Апостиль / Реестр</text>
        
        <rect x="360" y="12" width="15" height="15" fill="#E8F5E9" stroke="#A5D6A7"/>
        <text x="380" y="24" class="node">Complex Manual Signature</text>
        
        <rect x="600" y="12" width="15" height="15" fill="#F3E5F5" stroke="#CE93D8"/>
        <text x="620" y="24" class="node">Юридический статус / Вывод</text>
    </g>

    <!-- Nodes -->
    <!-- Document 1 -->
    <g transform="translate(50, 150)">
        <rect width="250" height="90" class="doc-box"/>
        <text x="15" y="25" class="text-bold">Дело № 1ra-834/09</text>
        <text x="15" y="45" class="node">Определение ВСП РМ (21.07.2009)</text>
        <text x="15" y="70" class="text-sm">SHA256: 47d0d04c2195...1804</text>
    </g>

    <!-- Document 2 -->
    <g transform="translate(50, 350)">
        <rect width="250" height="90" class="doc-box"/>
        <text x="15" y="25" class="text-bold">Сертификат C013564402308</text>
        <text x="15" y="45" class="node">CNDDCM РМ (05.04.2021)</text>
        <text x="15" y="70" class="text-sm">SHA256: 92e2f2b63c95...16f</text>
    </g>

    <!-- Apostille 1 -->
    <g transform="translate(380, 150)">
        <rect width="260" height="90" class="apostille-box"/>
        <text x="15" y="25" class="text-bold">Апостиль № CG0T6Y1TBUEL7</text>
        <text x="15" y="45" class="node">Секьюрити-код: 2013074491511</text>
        <text x="15" y="70" class="text-sm">Подписант: Mîrzac Iuliana (12.07.2022)</text>
    </g>

    <!-- Apostille 2 -->
    <g transform="translate(380, 350)">
        <rect width="260" height="90" class="apostille-box"/>
        <text x="15" y="25" class="text-bold">Апостиль № 90VS71FRKM4S3</text>
        <text x="15" y="45" class="node">Секьюрити-код: 2013073942632</text>
        <text x="15" y="70" class="text-sm">Подписант: Valeriu Frimu (02.06.2021)</text>
    </g>

    <!-- Signature 1 -->
    <g transform="translate(730, 150)">
        <rect width="260" height="90" class="sig-box"/>
        <text x="15" y="25" class="text-bold">Подпись на документе</text>
        <text x="15" y="45" class="node">"semnatura indescifrabila"</text>
        <text x="15" y="70" class="text-bold" fill="#2E7D32">[Complex Manual Signature]</text>
    </g>

    <!-- Signature 2 -->
    <g transform="translate(730, 350)">
        <rect width="260" height="90" class="sig-box"/>
        <text x="15" y="25" class="text-bold">Подпись И.О. Директора CNDDCM</text>
        <text x="15" y="45" class="node">Stela Pînzaru</text>
        <text x="15" y="70" class="text-bold" fill="#2E7D32">[Complex Manual Signature]</text>
    </g>

    <!-- Status / Output Nodes -->
    <g transform="translate(730, 500)">
        <rect width="260" height="90" class="status-box"/>
        <text x="15" y="25" class="text-bold">Юридический вывод</text>
        <text x="15" y="45" class="node">Подпись визуально подтверждена</text>
        <text x="15" y="70" class="text-sm">Не является 'unclear' (Jus Cogens)</text>
    </g>

    <!-- Edges / Connectors -->
    <!-- Doc 1 -> Apostille 1 -->
    <path d="M 300 195 L 370 195" class="edge"/>
    
    <!-- Apostille 1 -> Signature 1 -->
    <path d="M 640 195 L 720 195" class="edge"/>

    <!-- Signature 1 -> Status -->
    <path d="M 860 240 L 860 490" class="edge"/>

    <!-- Doc 2 -> Apostille 2 -->
    <path d="M 300 395 L 370 395" class="edge"/>

    <!-- Apostille 2 -> Signature 2 -->
    <path d="M 640 395 L 720 395" class="edge"/>

    <!-- Signature 2 -> Status -->
    <path d="M 860 440 L 860 490" class="edge"/>

</svg>
"""

os.makedirs("03_GRAPH_GRAPHICS", exist_ok=True)
with open("03_GRAPH_GRAPHICS/signature_evidence_graph.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("SVG vector schema successfully generated at 03_GRAPH_GRAPHICS/signature_evidence_graph.svg")
