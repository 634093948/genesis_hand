# Image Compositor Node for ComfyUI

A custom node for ComfyUI that provides an interactive canvas-based image composition interface with layer management.

## Features

### Interactive Canvas Editor
- Visual canvas interface for composing multiple images
- Real-time preview with background image support
- Automatic canvas sizing based on background image dimensions
- Aspect ratio preservation for accurate composition

### Layer Management
- Add multiple image layers via drag-and-drop or file selection
- Move layers by clicking and dragging on canvas
- Resize layers using the green handle at bottom-right corner
- Delete layers by clicking the red X button at top-right corner
- Toggle layer visibility with eye icon
- Adjust layer opacity with slider control
- View layer information (position, dimensions)

### Background Image
- Set any uploaded image as background
- Canvas automatically adapts to background image dimensions
- Background image is used as base for final composition

### On-Canvas Controls
- Green border around selected/active layer
- Green resize handle at bottom-right corner
- Red delete button (X) at top-right corner of each layer
- Click delete button to remove layer instantly

### Output
- Composited RGB image combining background and all visible layers
- Layer mask showing all layer positions
- Layer information metadata (JSON format)

## Usage

1. Add "Image Compositor" node to your workflow
2. Upload a background image using the background parameter
3. Click "Add Layer" button to upload layer images
4. Arrange layers on canvas:
   - Drag layers to reposition
   - Drag bottom-right green handle to resize
   - Click top-right red X to delete
5. Adjust layer properties in the layer list:
   - Toggle visibility with eye icon
   - Adjust opacity with slider
6. Connect outputs to other nodes for further processing

## Technical Details

### Canvas Coordinates
- All layer positions use logical coordinates matching background image dimensions
- Example: For 1024x1920 background, layer at (100, 100) is positioned at pixel (100, 100) in final output
- Canvas display auto-scales while maintaining coordinate accuracy

### Layer Data Structure
Each layer stores:
- `name`: Original filename
- `x`, `y`: Position in logical coordinates
- `width`, `height`: Layer dimensions
- `opacity`: 0.0 to 1.0
- `visible`: Boolean visibility flag
- `id`: Unique identifier

### Node Inputs
- `background`: Background image (required)
- `layers_data`: JSON string storing layer information (auto-managed)

### Node Outputs
- `composite`: Final RGB image with all layers composited
- `mask`: Binary mask showing layer positions
- `layer_info`: JSON metadata about composition

## Implementation Notes

### Canvas Size Management
- Canvas automatically reads background image dimensions
- Each node instance maintains independent canvas size
- Aspect ratio updates dynamically when background changes
- Maximum canvas height: 800px (scrollable for taller images)

### Layer Operations
- Delete operations invalidate pending image loads to prevent visual artifacts
- Render token system ensures only current layer state is displayed
- All operations update both canvas preview and backend layer data

### Coordinate System
- Frontend uses logical coordinates matching background dimensions
- Backend compositor directly uses these coordinates
- No coordinate transformation needed between frontend and backend

## File Structure

```
multi-image-manager/
├── __init__.py              # Node registration
├── nodes.py                 # Backend compositor logic
├── js/
│   └── image_compositor.js  # Frontend UI and canvas interaction
└── README.md               # This file
```

## API Reference

### Clear Button
Removes all layers from canvas. No confirmation dialog.

### Add Layer Button
Opens file picker to upload new layer image. Uploaded image is automatically positioned and scaled to fit canvas.

### Layer List Item
- Eye icon: Toggle visibility
- Opacity slider: Adjust transparency (0-100%)
- Red X button: Delete this layer

### Canvas Interactions
- Click and drag layer: Move position
- Drag green handle: Resize layer (maintains aspect ratio)
- Click red X button: Delete layer immediately

## Browser Compatibility

Tested on:
- Chrome/Edge (Chromium-based)
- Firefox
- Safari (WebKit-based)

Requires:
- HTML5 Canvas support
- ES6 JavaScript
- CSS Grid and Flexbox

## Known Limitations

- Maximum canvas display height: 800px
- Very large images may require scrolling
- Layer count limited by browser memory
- No undo/redo functionality

## Author

Created by: eddy

## License

See main ComfyUI license.
