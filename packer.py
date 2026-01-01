class GuillotinePacker:
    def __init__(self, bin_width, bin_height, rotation=True):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.rotation = rotation
        self.free_rectangles = [(0, 0, bin_width, bin_height)]  # x, y, w, h
        self.placed_rectangles = []

    def pack(self, rectangles):
        """
        rectangles: list of tuples (width, height, label/id)
        Sorts by area descending for better packing (heuristic).
        """
        # Sort by height then width (or area)
        sorted_rects = sorted(rectangles, key=lambda r: max(r[0], r[1]), reverse=True)
        
        for rect in sorted_rects:
            w, h = rect[0], rect[1]
            placed = False
            
            # Find a free rectangle that fits
            best_rect_idx = -1
            best_score = float('inf')
            best_w, best_h = w, h
            best_rotated = False

            for i, free_rect in enumerate(self.free_rectangles):
                fx, fy, fw, fh = free_rect
                
                # Check normal orientation
                if fw >= w and fh >= h:
                    score = min(fw - w, fh - h) # Best Short Side Fit
                    # or score = fw * fh - w * h # Best Area Fit
                    if score < best_score:
                        best_score = score
                        best_rect_idx = i
                        best_w, best_h = w, h
                        best_rotated = False
                
                # Check rotated orientation
                if self.rotation and fw >= h and fh >= w:
                    score = min(fw - h, fh - w)
                    if score < best_score:
                        best_score = score
                        best_rect_idx = i
                        best_w, best_h = h, w
                        best_rotated = True
            
            if best_rect_idx != -1:
                # Place the rectangle
                fx, fy, fw, fh = self.free_rectangles.pop(best_rect_idx)
                self.placed_rectangles.append({
                    'x': fx, 'y': fy, 
                    'w': best_w, 'h': best_h, 
                    'label': rect[2] if len(rect) > 2 else '',
                    'rotated': best_rotated
                })
                
                # Split the remaining area
                # Split strategies: Shorter Axis Split (SAS) or Longer Axis Split (LAS)
                # Here we use a heuristic based on remaining sides
                
                # New free rectangles
                # Split vertically (cut x-axis) vs horizontally (cut y-axis)
                
                # Option 1: Top remaining and Right remaining (Vertical cut priority)
                # Right: (fx + best_w, fy, fw - best_w, fh)
                # Top:   (fx, fy + best_h, best_w, fh - best_h)
                
                # Option 2: Bottom remaining and Right remaining (Horizontal cut priority)
                # Right: (fx + best_w, fy, fw - best_w, best_h)
                # Top:   (fx, fy + best_h, fw, fh - best_h)
                
                # We choose the split that creates the larger free rectangle (LAS) or maximizes specific aspect ratios.
                # Simple strategy: Minimize the smaller dimension of the leftovers? No, we want BIG leftovers.
                
                free_w = fw - best_w
                free_h = fh - best_h
                
                if free_w > free_h: # Split vertically to keep a large width piece? 
                    # Actually standard Guillotine usually picks one axis.
                    # Let's use MAXRECTS approach simplified or just basic split.
                    # Let's stick to Short Axis Split rule for Guillotine:
                    
                    if free_w < free_h: 
                         # Split horizontally
                        new_right = (fx + best_w, fy, fw - best_w, best_h)
                        new_top = (fx, fy + best_h, fw, fh - best_h)
                    else:
                        # Split vertically
                        new_right = (fx + best_w, fy, fw - best_w, fh)
                        new_top = (fx, fy + best_h, best_w, fh - best_h)
                else:
                     if free_w < free_h:
                        new_right = (fx + best_w, fy, fw - best_w, best_h)
                        new_top = (fx, fy + best_h, fw, fh - best_h)
                     else:
                        new_right = (fx + best_w, fy, fw - best_w, fh)
                        new_top = (fx, fy + best_h, best_w, fh - best_h)

                # Filter out valid new rectangles
                if new_right[2] > 0 and new_right[3] > 0:
                    self.free_rectangles.append(new_right)
                if new_top[2] > 0 and new_top[3] > 0:
                    self.free_rectangles.append(new_top)
                    
            else:
                # Could not fit
                print(f"Could not fit rectangle {w}x{h}")

        return self.placed_rectangles

