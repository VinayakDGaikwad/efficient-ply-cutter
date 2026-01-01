class GuillotinePacker:
    def __init__(self, bin_width, bin_height, rotation=True):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.rotation = rotation
        self.placements = []
        self.shelves = []  # List of {y, height, current_x}

    def pack(self, rectangles):
        """
        rectangles: list of tuples (width, height) or (width, height, label/data)
        Implements a Shelf-based First Fit Decreasing Height (FFDH) algorithm.
        This ensures 'continuous boundaries' (strips/levels) for easy cutting.
        """
        # Prepare items with tracking ID to preserve return order or association if needed
        # (Though current app just re-lists them, tracking index helps stability)
        items = []
        for i, r in enumerate(rectangles):
            items.append({
                'w': r[0],
                'h': r[1],
                'id': i,
                'data': r[2] if len(r) > 2 else None
            })

        # Pre-process orientations if rotation is allowed.
        # Strategy: Orient all items to be 'flat' (width >= height) to minimize shelf height
        # and maximize number of strips. This generally improves packing for guillotine cuts.
        if self.rotation:
            for item in items:
                if item['h'] > item['w']:
                    item['w'], item['h'] = item['h'], item['w']
                    item['started_rotated'] = True # Mark that we flipped it from input
                else:
                    item['started_rotated'] = False
        else:
            for item in items:
                item['started_rotated'] = False

        # Sort by height descending (FFDH Requirement)
        # Secondary sort by width descending helps fill shelves better
        items.sort(key=lambda x: (x['h'], x['w']), reverse=True)

        self.shelves = []
        self.placements = []

        for item in items:
            placed = False
            
            # 1. Try to fit in existing shelves
            # We look for a BEST FIT shelf to minimize wasted width, 
            # or First Fit. FFDH is First Fit. Let's try First Fit first as it's standard.
            for shelf in self.shelves:
                # Check if item fits in this shelf
                # We also assume the item is currently 'flat' preference.
                # But if it doesn't fit 'flat' in width, maybe it fits 'tall'?
                # (Only if rotation allowed and item fits vertically within shelf height)
                
                fits_flat = (self.bin_width - shelf['current_x'] >= item['w']) and (shelf['height'] >= item['h'])
                
                fits_rotated = False
                if self.rotation:
                    # Check if fits rotated (swapped w and h)
                    # Rotated width = item['h'], Rotated height = item['w']
                    if (self.bin_width - shelf['current_x'] >= item['h']) and (shelf['height'] >= item['w']):
                        fits_rotated = True
                
                # Decision logic:
                # If fits both, prefer the one that matches shelf height better? 
                # Or prefer flat to save horizontal space?
                # Actually, if it fits flat, it usually uses more width but less height req.
                # Shelf height is fixed. We just need to fit inside.
                # We prefer fitting flat because item['h'] is <= item['w'] (pre-sorted),
                # so specific orientation might naturally align better?
                # Actually, check which one wastes less vertical shelf space?
                # Shelf height is fixed. Item height is used. Waste is (Shelf H - Item H).
                # We want to minimize (Shelf H - Item H). 
                # So choose orientation with height closest to Shelf Height.
                
                if fits_flat or fits_rotated:
                    # Determine best orientation for this shelf
                    use_rotated = False
                    if fits_flat and fits_rotated:
                        waste_flat = shelf['height'] - item['h']
                        waste_rotated = shelf['height'] - item['w']
                        # Pick minimal waste
                        if waste_rotated < waste_flat:
                            use_rotated = True
                    elif fits_rotated:
                        use_rotated = True
                    # else fits_flat is True
                    
                    # Place it
                    w_used = item['h'] if use_rotated else item['w']
                    h_used = item['w'] if use_rotated else item['h']
                    
                    # Calculate if it is effectively rotated relative to INPUT
                    # item['started_rotated'] is True if we swapped input (w,h) -> (h,w)
                    # use_rotated is True if we swapped AGAIN for placement
                    # Effective rotation = started_rotated XOR use_rotated
                    is_rotated_final = item['started_rotated'] ^ use_rotated
                    
                    self.placements.append({
                        'x': shelf['current_x'],
                        'y': shelf['y'],
                        'w': w_used,
                        'h': h_used,
                        'rotated': is_rotated_final,
                        'label': item['data']
                    })
                    
                    shelf['current_x'] += w_used
                    placed = True
                    break
            
            if not placed:
                # 2. Create new shelf
                # If we couldn't fit in existing shelves, we start a new one.
                # We prefer 'flat' orientation for new shelf to minimize shelf height
                # (since we sorted by height desc, this is the smallest max height we can verify).
                
                # Check bounds
                new_y = 0
                if self.shelves:
                    last_shelf = self.shelves[-1]
                    new_y = last_shelf['y'] + last_shelf['height']
                
                # Try placing Flat
                w_used = item['w']
                h_used = item['h']
                
                can_place_flat = (new_y + h_used <= self.bin_height) and (w_used <= self.bin_width)
                
                # Try placing Rotated (Tall) - Only if it greatly benefits or flat fails?
                # Actually, with FFDH, we sorted by H. We want next shelf to be determined by current item.
                # The item is oriented Flat (h <= w).
                # If we rotate it Tall, H increases. Shelf gets taller. Bad.
                # EXCEPT if Flat width > bin_width. Then we MUST rotate.
                
                use_rotated = False
                if not can_place_flat:
                    if self.rotation and (new_y + item['w'] <= self.bin_height) and (item['h'] <= self.bin_width):
                         use_rotated = True
                    else:
                        # Cannot fit
                        print(f"Cannot pack item {item['w']}x{item['h']}")
                        continue
                
                # If both valid, strictly prefer Flat to minimize Y progression?
                # Yes.
                
                final_w = item['h'] if use_rotated else item['w']
                final_h = item['w'] if use_rotated else item['h']
                
                self.shelves.append({
                    'y': new_y,
                    'height': final_h,
                    'current_x': final_w
                })
                
                is_rotated_final = item['started_rotated'] ^ use_rotated
                
                self.placements.append({
                    'x': 0,
                    'y': new_y,
                    'w': final_w,
                    'h': final_h,
                    'rotated': is_rotated_final,
                    'label': item['data']
                })

        return self.placements
