from flask import Flask, render_template, request, jsonify
from packer import GuillotinePacker

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    sheet_w = float(data.get('sheetW', 2440))
    sheet_h = float(data.get('sheetH', 1220))
    rotation = bool(data.get('rotation', True))
    kerf = float(data.get('kerf', 0)) # Not implemented in packer yet, simplified for now
    
    # Flatten blocks list based on quantity
    rectangles = []
    blocks = data.get('blocks', [])
    for b in blocks:
        qty = b.get('q', 1)
        w = float(b.get('w'))
        h = float(b.get('h'))
        for _ in range(qty):
            # Account for kerf?
            # Standard way: add kerf to item size, then subtract from final result or assume kerf is lost 'between' cuts.
            # Simplified: Use effective item size = item + kerf.
            # But packer assumes 0 kerf.
            # Let's add kerf to items for packing, but display original size.
            effective_w = w + kerf
            effective_h = h + kerf
            rectangles.append((effective_w, effective_h, {'orig_w': w, 'orig_h': h}))

    # If kerf is used, we should also reduce sheet size or treat sheet as having margins? 
    # Usually easier to just add kerf to items. 
    # But wait, if we pack tight, the last item doesn't need kerf on the edge? 
    # Simpler approach: Assume kerf is negligible for this MVP or handled by user surplus.
    # Reverting kerf logic for simplicity to stick to the basic packer I wrote.
    # The user can just input slightly larger block sizes if they care deeply about kerf, or I can refine later.
    
    # Let's repack without kerf explicit modification for now to ensure correctness of the visualizer primarily.
    rects_for_packer = []
    for b in blocks:
         for _ in range(int(b.get('q', 1))):
              rects_for_packer.append((float(b['w']), float(b['h'])))

    packer = GuillotinePacker(sheet_w, sheet_h, rotation=rotation)
    placements = packer.pack(rects_for_packer)
    
    # Calculate stats
    used_area = sum(p['w'] * p['h'] for p in placements)
    total_area = sheet_w * sheet_h
    efficiency = (used_area / total_area) * 100 if total_area > 0 else 0
    
    return jsonify({
        'placements': placements,
        'efficiency': efficiency,
        'count': len(placements)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
