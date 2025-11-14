import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

function chainCallback(object, property, callback) {
    if (!object) return;
    if (property in object) {
        const orig = object[property];
        object[property] = function () {
            const r = orig.apply(this, arguments);
            try { callback.apply(this, arguments); } catch (e) { console.error(e); }
            return r;
        };
    } else {
        object[property] = callback;
    }
}

const layersStorage = new Map();

app.registerExtension({
    name: "eddy.ImageCompositor",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ImageCompositor") return;

        chainCallback(nodeType.prototype, "onNodeCreated", function () {
            try {
                const layersWidget = this.widgets?.find(w => w.name === "layers_data");
                const bgWidget = this.widgets?.find(w => w.name === "background");

                if (!layersWidget) return;

                // Make layers_data hidden
                layersWidget.type = "customtext";
                layersWidget.hidden = true;

                const nodeId = this.id;
                const node = this;
                layersStorage.set(nodeId, []);

                // Create main container
                const element = document.createElement("div");
                element.style.cssText = `
                    width: 100%;
                    height: 100%;
                    background: #1a1a1a;
                    border-radius: 4px;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                    box-sizing: border-box;
                    padding: 0;
                `;

                // Toolbar
                const toolbar = document.createElement("div");
                toolbar.style.cssText = `
                display: flex;
                gap: 6px;
                padding: 6px;
                background: #252525;
                flex: 0 0 auto;
            `;

                const addBtn = document.createElement("button");
                addBtn.textContent = "➕ Add Layer";
                addBtn.style.cssText = `
                flex: 1;
                padding: 6px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            `;
                addBtn.onclick = () => {
                    console.log("[ImageCompositor] Add Layer clicked");
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = "image/*";
                    input.onchange = async (e) => {
                        const file = e.target.files[0];
                        if (file) {
                            console.log("[ImageCompositor] File selected:", file.name);
                            addBtn.textContent = "⏳ Uploading...";
                            addBtn.disabled = true;
                            await uploadLayer(file, node, layersWidget, compositorWidget);
                            addBtn.textContent = "➕ Add Layer";
                            addBtn.disabled = false;
                        }
                    };
                    input.click();
                };

                const clearBtn = document.createElement("button");
                clearBtn.textContent = "🗑️ Clear";
                clearBtn.style.cssText = `
                padding: 6px 12px;
                background: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            `;

                toolbar.appendChild(addBtn);
                toolbar.appendChild(clearBtn);

                // Canvas container with auto height based on aspect ratio
                const canvasContainer = document.createElement("div");
                canvasContainer.style.cssText = `
                    position: relative;
                    width: 100%;
                    height: auto;
                    max-height: 800px;
                    overflow: auto;
                    flex: 0 0 auto;
                    aspect-ratio: 1 / 1;
                    background: #2b2b2b url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect fill="%23333" width="10" height="10"/><rect fill="%23333" x="10" y="10" width="10" height="10"/><rect fill="%23222" x="10" width="10" height="10"/><rect fill="%23222" y="10" width="10" height="10"/></svg>');
                `;

                const canvas = document.createElement("canvas");
                // Backing store will be updated to match aspect ratio on bg load
                canvas.width = 1024;
                canvas.height = 1024;
                canvas.style.cssText = `
                width: 100%;
                height: 100%;
                display: block;
                cursor: crosshair;
            `;
                canvasContainer.appendChild(canvas);

                // Layers list
                const layersList = document.createElement("div");
                layersList.style.cssText = `
                padding: 8px;
                min-height: 80px;
                max-height: 200px;
                overflow-y: auto;
                background: #1a1a1a;
                border-top: 2px solid #444;
                flex: 0 0 auto;
                display: block;
            `;

                element.appendChild(toolbar);
                element.appendChild(canvasContainer);
                element.appendChild(layersList);

                // Add DOM widget first
                const compositorWidget = this.addDOMWidget("compositor", "div", element, {
                    serialize: false,
                    hideOnZoom: false,
                });

                // Reserved height for initial layout (canvas will auto-adjust based on aspect ratio)
                // 现在只用于初始化，实际高度由CSS控制
                const reservedHeight = 626;

                // Spacer AFTER DOM widget to prevent gap at top
                const spacer = this.addWidget("label", "", "", () => { }, { serialize: false });
                spacer.label = "";
                spacer.draw = function () { };
                spacer.computeSize = (w) => {
                    return [w, 0]; // Return 0, DOM widget handles the height
                };

                // Store references (node is read-only, use closure variable instead)
                compositorWidget.canvas = canvas;
                compositorWidget.canvasContainer = canvasContainer;
                compositorWidget.layersList = layersList;
                compositorWidget.layersWidget = layersWidget;
                compositorWidget.bgWidget = bgWidget;
                compositorWidget._nodeRef = node; // Use custom property for node reference
                compositorWidget.canvasSize = { width: 1024, height: 1024 }; // Per-node canvas size

                // Make DOM widget reserve fixed height
                compositorWidget.computeSize = function (width) {
                    this.computedHeight = reservedHeight;
                    return [width, reservedHeight];
                };

                // Ensure node size is at least the reserved height (prevents collapse/overflow)
                const minW = 380;
                const minH = reservedHeight + 20;
                const newW = Math.max(this.size[0], minW);
                const newH = Math.max(this.size[1], minH);
                this.setSize([newW, newH]);

                // Bind Clear button now that compositorWidget exists
                clearBtn.onclick = () => {
                    // Reset stored layers
                    layersStorage.set(nodeId, []);
                    updateLayersWidget(layersWidget, []);
                    // Reset any ongoing interactions
                    compositorWidget._draggedLayer = null;
                    compositorWidget._resizing = false;
                    compositorWidget._resizeLayer = null;
                    // Invalidate any pending image onload draws
                    compositorWidget._renderToken = (compositorWidget._renderToken || 0) + 1;
                    // Re-render UI
                    renderCanvas(compositorWidget);
                    renderLayersList(compositorWidget);
                };

                // Initial render
                if (bgWidget && bgWidget.value) {
                    const bgImg = new Image();
                    bgImg.crossOrigin = "anonymous";
                    bgImg.src = api.apiURL(`/view?filename=${encodeURIComponent(bgWidget.value)}&type=input&t=${Date.now()}`);
                    bgImg.onload = () => {
                        if (bgImg.naturalWidth && bgImg.naturalHeight) {
                            compositorWidget.canvasSize = { width: bgImg.naturalWidth, height: bgImg.naturalHeight };
                            console.log("[ImageCompositor] Initial canvasSize:", compositorWidget.canvasSize);
                            // Update canvas container aspect ratio
                            const aspectRatio = bgImg.naturalWidth / bgImg.naturalHeight;
                            canvasContainer.style.aspectRatio = `${bgImg.naturalWidth} / ${bgImg.naturalHeight}`;
                            console.log("[ImageCompositor] Set aspect-ratio:", aspectRatio);
                        }
                        renderCanvas(compositorWidget);
                        renderLayersList(compositorWidget);
                    };
                    bgImg.onerror = () => {
                        console.error("[ImageCompositor] Failed to load background for canvasSize init");
                        renderCanvas(compositorWidget);
                        renderLayersList(compositorWidget);
                    };
                } else {
                    // No background yet, render with default size
                    setTimeout(() => {
                        renderCanvas(compositorWidget);
                        renderLayersList(compositorWidget);
                    }, 100);
                }

                // Re-render when node is resized (zoom/layout changes)
                const origOnResize = this.onResize;
                this.onResize = function (size) {
                    const r = origOnResize?.apply(this, arguments);
                    renderCanvas(compositorWidget);
                    return r;
                };

                // Canvas interaction handlers
                canvas.addEventListener('pointerdown', (e) => {
                    handleCanvasPointerDown(e, compositorWidget);
                    e.stopPropagation();
                });

                canvas.addEventListener('pointermove', (e) => {
                    if (compositorWidget._draggedLayer || compositorWidget._resizing) {
                        handleCanvasPointerMove(e, compositorWidget);
                        e.stopPropagation();
                    }
                });

                canvas.addEventListener('pointerup', (e) => {
                    if (compositorWidget._draggedLayer || compositorWidget._resizing) {
                        handleCanvasPointerUp(compositorWidget);
                        e.stopPropagation();
                    }
                });

                canvas.addEventListener('pointerleave', () => {
                    handleCanvasPointerUp(compositorWidget);
                });

                // Background change handler
                if (bgWidget && typeof bgWidget.callback === "function") {
                    const origOnChange = bgWidget.callback;
                    bgWidget.callback = function (value) {
                        if (origOnChange) origOnChange.call(this, value);
                        if (value) {
                            try {
                                const bgImg = new Image();
                                bgImg.crossOrigin = "anonymous";
                                bgImg.src = api.apiURL(`/view?filename=${encodeURIComponent(value)}&type=input&t=${Date.now()}`);
                                bgImg.onload = () => {
                                    if (bgImg.naturalWidth && bgImg.naturalHeight) {
                                        compositorWidget.canvasSize = { width: bgImg.naturalWidth, height: bgImg.naturalHeight };
                                        console.log("[ImageCompositor] Background changed, canvasSize:", compositorWidget.canvasSize);
                                        // Update canvas container aspect ratio
                                        const aspectRatio = bgImg.naturalWidth / bgImg.naturalHeight;
                                        canvasContainer.style.aspectRatio = `${bgImg.naturalWidth} / ${bgImg.naturalHeight}`;
                                        console.log("[ImageCompositor] Set aspect-ratio:", aspectRatio);
                                    }
                                    renderCanvas(compositorWidget);
                                };
                            } catch (e) {
                                console.error("ImageCompositor bg load error:", e);
                                renderCanvas(compositorWidget);
                            }
                        } else {
                            renderCanvas(compositorWidget);
                        }
                    };
                }

                // Watch layersWidget for changes
                const origLayersCallback = layersWidget.callback;
                layersWidget.callback = function(value) {
                    if (origLayersCallback) origLayersCallback.call(this, value);
                    if (value) {
                        try {
                            const layers = JSON.parse(value);
                            layersStorage.set(nodeId, layers);
                            renderCanvas(compositorWidget);
                            renderLayersList(compositorWidget);
                        } catch (e) {
                            console.error("[ImageCompositor] Failed to sync layers:", e);
                        }
                    }
                };

                // Cleanup
                const onRemoved = this.onRemoved;
                this.onRemoved = function () {
                    layersStorage.delete(nodeId);
                    return onRemoved?.apply(this, arguments);
                };

                // Load saved state
                const onConfigure = this.onConfigure;
                this.onConfigure = function(info) {
                    const result = onConfigure?.apply(this, arguments);
                    if (layersWidget.value) {
                        try {
                            const layers = JSON.parse(layersWidget.value);
                            layersStorage.set(nodeId, layers);
                            renderCanvas(compositorWidget);
                            renderLayersList(compositorWidget);
                        } catch (e) {
                            console.error("Failed to parse layers:", e);
                        }
                    }
                    return result;
                };

            } catch (err) {
                console.error("ImageCompositor onNodeCreated error:", err);
            }
        });
    }
});

async function uploadLayer(file, node, layersWidget, widget) {
    console.log("[ImageCompositor] uploadLayer called", file.name);
    const formData = new FormData();
    formData.append("image", file);
    formData.append("type", "input");
    formData.append("overwrite", "false");

    try {
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body: formData
        });

        console.log("[ImageCompositor] Upload response:", resp.status);

        if (resp.ok) {
            const data = await resp.json();
            console.log("[ImageCompositor] Uploaded:", data.name);

            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = api.apiURL(`/view?filename=${encodeURIComponent(data.name)}&type=input&t=${Date.now()}`);
            img.onerror = (e) => {
                console.error("[ImageCompositor] Image load failed:", e);
            };
            img.onload = () => {
                console.log("[ImageCompositor] Image loaded:", img.naturalWidth, "x", img.naturalHeight);
                console.log("[ImageCompositor] Current canvasSize:", widget.canvasSize);
                const layers = layersStorage.get(node.id) || [];
                const maxW = Math.floor(widget.canvasSize.width * 0.6);
                const maxH = Math.floor(widget.canvasSize.height * 0.6);
                let w = img.naturalWidth || 200;
                let h = img.naturalHeight || 200;
                const scale = Math.min(1, maxW / w, maxH / h);
                w = Math.floor(w * scale);
                h = Math.floor(h * scale);

                const newLayer = {
                    id: Date.now() + Math.random(),
                    name: data.name,
                    x: 100,
                    y: 100,
                    width: w,
                    height: h,
                    opacity: 1.0,
                    visible: true
                };

                layers.push(newLayer);
                console.log("[ImageCompositor] Layer added:", newLayer);
                console.log("[ImageCompositor] Total layers:", layers.length);

                console.log("[uploadLayer] Storing layers for node:", node.id);
                layersStorage.set(node.id, layers);
                console.log("[uploadLayer] layersStorage now has:", Array.from(layersStorage.keys()));
                updateLayersWidget(layersWidget, layers);
                
                // Re-apply aspect ratio to prevent reset
                if (widget.canvasSize && widget.canvasSize.width && widget.canvasSize.height) {
                    const aspectRatio = widget.canvasSize.width / widget.canvasSize.height;
                    widget.canvasContainer.style.aspectRatio = `${widget.canvasSize.width} / ${widget.canvasSize.height}`;
                    console.log("[uploadLayer] Re-applied aspect-ratio:", aspectRatio);
                }
                
                renderCanvas(widget);
                renderLayersList(widget);
            };
        } else {
            console.error("[ImageCompositor] Upload failed with status:", resp.status);
        }
    } catch (error) {
        console.error("[ImageCompositor] Upload error:", error);
        alert("Upload failed: " + error.message);
    }
}

function handleCanvasPointerDown(e, widget) {
    const rect = widget.canvas.getBoundingClientRect();
    const scaleX = widget.canvasSize.width / rect.width;
    const scaleY = widget.canvasSize.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    const layers = layersStorage.get(widget._nodeRef.id) || [];

    for (let i = layers.length - 1; i >= 0; i--) {
        const layer = layers[i];
        if (!layer.visible) continue;

        const isInLayer = x >= layer.x && x <= layer.x + layer.width &&
                          y >= layer.y && y <= layer.y + layer.height;

        // hit test: delete button on top-right corner (20x20 logical pixels)
        const isOnDelete = x >= layer.x + layer.width - 20 &&
                           x <= layer.x + layer.width &&
                           y >= layer.y && y <= layer.y + 20;

        const isOnResize = x >= layer.x + layer.width - 20 &&
                           x <= layer.x + layer.width &&
                           y >= layer.y + layer.height - 20 &&
                           y <= layer.y + layer.height;

        if (isOnDelete) {
            layers.splice(i, 1);
            layersStorage.set(widget._nodeRef.id, layers);
            updateLayersWidget(widget.layersWidget, layers);
            widget._renderToken = (widget._renderToken || 0) + 1;
            renderCanvas(widget);
            renderLayersList(widget);
            e.stopPropagation();
            return;
        } else if (isOnResize) {
            widget._resizing = true;
            widget._resizeLayer = layer;
            widget._dragOffset = { x: x - (layer.x + layer.width), y: y - (layer.y + layer.height) };
            e.stopPropagation();
            return;
        } else if (isInLayer) {
            widget._draggedLayer = layer;
            widget._dragOffset = { x: x - layer.x, y: y - layer.y };
            e.stopPropagation();
            return;
        }
    }
}

function handleCanvasPointerMove(e, widget) {
    const rect = widget.canvas.getBoundingClientRect();
    const scaleX = widget.canvasSize.width / rect.width;
    const scaleY = widget.canvasSize.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    if (widget._resizing && widget._resizeLayer) {
        widget._resizeLayer.width = Math.max(50, x - widget._resizeLayer.x);
        widget._resizeLayer.height = Math.max(50, y - widget._resizeLayer.y);
        updateLayersWidget(widget.layersWidget, layersStorage.get(widget._nodeRef.id) || []);
        renderCanvas(widget);
        e.stopPropagation();
    } else if (widget._draggedLayer) {
        widget._draggedLayer.x = Math.max(0, Math.min(widget.canvasSize.width - widget._draggedLayer.width, x - widget._dragOffset.x));
        widget._draggedLayer.y = Math.max(0, Math.min(widget.canvasSize.height - widget._draggedLayer.height, y - widget._dragOffset.y));
        updateLayersWidget(widget.layersWidget, layersStorage.get(widget._nodeRef.id) || []);
        renderCanvas(widget);
        e.stopPropagation();
    }
}

function handleCanvasPointerUp(widget) {
    widget._draggedLayer = null;
    widget._resizing = false;
    widget._resizeLayer = null;
}

function renderCanvas(widget) {
    // Maintain aspect ratio to prevent reset
    if (widget.canvasSize && widget.canvasSize.width && widget.canvasSize.height && widget.canvasContainer) {
        const aspectRatio = widget.canvasSize.width / widget.canvasSize.height;
        widget.canvasContainer.style.aspectRatio = `${widget.canvasSize.width} / ${widget.canvasSize.height}`;
    }
    
    const canvas = widget.canvas;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Independent scaling to avoid distortion and keep coordinates consistent
    const scaleX = canvas.width / widget.canvasSize.width;
    const scaleY = canvas.height / widget.canvasSize.height;
    const bgWidget = widget.bgWidget;
    const layers = layersStorage.get(widget._nodeRef.id) || [];
    // Capture a render token to invalidate older async draws (e.g., after Clear)
    const token = widget._renderToken || 0;

    if (bgWidget && bgWidget.value) {
        const bgImg = new Image();
        bgImg.crossOrigin = "anonymous";
        bgImg.src = api.apiURL(`/view?filename=${encodeURIComponent(bgWidget.value)}&type=input&t=${Date.now()}`);
        bgImg.onload = () => {
            if ((widget._renderToken || 0) !== token) return; // stale
            ctx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
            drawLayers();
        };
    } else {
        drawLayers();
    }

    function drawLayers() {
        layers.forEach(layer => {
            if (!layer.visible) return;

            const layerImg = new Image();
            layerImg.crossOrigin = "anonymous";
            layerImg.src = api.apiURL(`/view?filename=${encodeURIComponent(layer.name)}&type=input&t=${Date.now()}`);
            layerImg.onload = () => {
                if ((widget._renderToken || 0) !== token) return; // stale
                ctx.save();
                ctx.globalAlpha = layer.opacity;
                ctx.drawImage(
                    layerImg,
                    Math.round(layer.x * scaleX),
                    Math.round(layer.y * scaleY),
                    Math.round(layer.width * scaleX),
                    Math.round(layer.height * scaleY)
                );
                ctx.restore();

                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.strokeRect(
                    Math.round(layer.x * scaleX),
                    Math.round(layer.y * scaleY),
                    Math.round(layer.width * scaleX),
                    Math.round(layer.height * scaleY)
                );

                ctx.fillStyle = '#00ff00';
                const handleSize = Math.max(10, Math.round(20 * Math.min(scaleX, scaleY)));
                ctx.fillRect(
                    Math.round((layer.x + layer.width) * scaleX - handleSize),
                    Math.round((layer.y + layer.height) * scaleY - handleSize),
                    handleSize,
                    handleSize
                );

                // draw delete button (top-right corner) with red square and white X
                const delSize = Math.max(12, Math.round(18 * Math.min(scaleX, scaleY)));
                const delX = Math.round((layer.x + layer.width) * scaleX - delSize);
                const delY = Math.round(layer.y * scaleY);
                ctx.fillStyle = '#e53935';
                ctx.fillRect(delX, delY, delSize, delSize);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(delX + 4, delY + 4);
                ctx.lineTo(delX + delSize - 4, delY + delSize - 4);
                ctx.moveTo(delX + delSize - 4, delY + 4);
                ctx.lineTo(delX + 4, delY + delSize - 4);
                ctx.stroke();
            };
        });
    }
}

function renderLayersList(widget) {
    const layersList = widget.layersList;
    const nodeId = widget._nodeRef.id;
    console.log("[renderLayersList] nodeId:", nodeId);
    const layers = layersStorage.get(nodeId) || [];
    console.log("[renderLayersList] layers count:", layers.length);
    console.log("[renderLayersList] layersStorage has:", Array.from(layersStorage.keys()));
    layersList.innerHTML = "";

    if (layers.length === 0) {
        layersList.innerHTML = '<div style="color: #888; text-align: center; padding: 10px;">No layers</div>';
        return;
    }

    layers.forEach((layer, index) => {
        try {
            console.log("[renderLayersList] Rendering layer", index, layer.name);
            const item = document.createElement("div");
            item.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px;
            background: #333;
            margin-bottom: 4px;
            border-radius: 3px;
        `;

        const visBtn = document.createElement("button");
        visBtn.textContent = layer.visible ? "👁️" : "🚫";
        visBtn.style.cssText = `background: none; border: none; cursor: pointer; font-size: 16px;`;
        visBtn.onclick = () => {
            layer.visible = !layer.visible;
            updateLayersWidget(widget.layersWidget, layers);
            renderCanvas(widget);
            renderLayersList(widget);
        };

        const info = document.createElement("div");
        info.style.cssText = `flex: 1; color: white; font-size: 11px;`;
        info.innerHTML = `
            <div style="font-weight: bold;">${layer.name}</div>
            <div style="color: #888;">x:${Math.round(layer.x)} y:${Math.round(layer.y)} ${Math.round(layer.width)}×${Math.round(layer.height)}</div>
        `;

        const opacitySlider = document.createElement("input");
        opacitySlider.type = "range";
        opacitySlider.min = "0";
        opacitySlider.max = "100";
        opacitySlider.value = layer.opacity * 100;
        opacitySlider.style.cssText = `width: 60px;`;
        opacitySlider.oninput = (e) => {
            layer.opacity = e.target.value / 100;
            updateLayersWidget(widget.layersWidget, layers);
            renderCanvas(widget);
        };

        const delBtn = document.createElement("button");
        delBtn.textContent = "✕";
        delBtn.style.cssText = `
            background: #f44336;
            color: white;
            border: none;
            border-radius: 3px;
            width: 24px;
            height: 24px;
            cursor: pointer;
        `;
        delBtn.onclick = () => {
            layers.splice(index, 1);
            // Invalidate pending draws
            widget._renderToken = (widget._renderToken || 0) + 1;
            updateLayersWidget(widget.layersWidget, layers);
            renderCanvas(widget);
            renderLayersList(widget);
        };

            item.appendChild(visBtn);
            item.appendChild(info);
            item.appendChild(opacitySlider);
            item.appendChild(delBtn);
            layersList.appendChild(item);
            console.log("[renderLayersList] Layer", index, "rendered successfully");
        } catch (err) {
            console.error("[renderLayersList] Error rendering layer", index, err);
        }
    });
}

function updateLayersWidget(widget, layers) {
    if (widget) widget.value = JSON.stringify(layers);
}
