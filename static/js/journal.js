
    let isOpen3D = false;
    let isAnimating3D = false;
    let activeWritingArea = null;
    const journal3d = document.getElementById('journal3d');
    const leftHalf3d = document.getElementById('leftHalf');
    const rightWing3d = document.getElementById('rightWing');
    const btnToggle3d = document.getElementById('btn-journal-toggle');
    const allPages = document.querySelectorAll('.journal-spotlight .page');

    const OPEN_DUR = 1200;

    window.toggleJournal3D = function () {
        if (isAnimating3D) return;
        isAnimating3D = true;
        isOpen3D = !isOpen3D;

        const toolsPanel = document.querySelector('.journal-tools-panel');
        const editorToolbar = document.getElementById('journalEditorToolbar');
        const btnJournalLabel = btnToggle3d && btnToggle3d.querySelector('.btn-journal-label');

        if (isOpen3D) {
            journal3d.classList.add('spread-open');
            leftHalf3d.classList.add('wing-open');
            rightWing3d.classList.add('wing-open');
            if (btnJournalLabel) btnJournalLabel.textContent = 'Close Journal';
            setTimeout(() => {
                isAnimating3D = false;
                if (toolsPanel) toolsPanel.classList.add('is-visible');
                if (editorToolbar) editorToolbar.classList.add('is-visible');
                const btnSave = document.getElementById('btn-save-entry');
                if (btnSave) btnSave.classList.add('visible');
            }, OPEN_DUR);
        } else {
            if (toolsPanel) toolsPanel.classList.remove('is-visible');
            if (editorToolbar) editorToolbar.classList.remove('is-visible');
            const btnSave = document.getElementById('btn-save-entry');
            if (btnSave) btnSave.classList.remove('visible');
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
                    const label = btnToggle3d && btnToggle3d.querySelector('.btn-journal-label');
                    if (label) label.textContent = 'Open Journal';
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

    window.setStyle3D = function (style) {
        const allPotential = document.querySelectorAll('.journal-spotlight .page, .journal-spotlight .page-front, .journal-spotlight .page-back, .journal-spotlight .wing, .journal-spotlight .cover-inside');
        allPotential.forEach(el => el.classList.remove('style-grid', 'style-blank', 'style-lined'));
        const faces = document.querySelectorAll('.journal-spotlight .page-front, .journal-spotlight .page-back');
        faces.forEach(el => el.classList.add('style-' + style));

        document.querySelectorAll('.style-picker-h .style-btn-h').forEach(btn => {
            const active = btn.dataset.style === style;
            btn.classList.toggle('is-active', active);
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        });

        // Dynamic font-size visibility: only visible on 'blank' (freeform) style
        const sizeSection = document.getElementById('tb-font-size-section');
        const sizeDivider = document.getElementById('tb-font-size-divider');
        if (sizeSection && sizeDivider) {
            if (style === 'blank') {
                sizeSection.style.display = 'flex';
                sizeDivider.style.display = 'block';
            } else {
                sizeSection.style.display = 'none';
                sizeDivider.style.display = 'none';
            }
        }
    };

    window.addEventListener('load', () => {
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
            if (e.key === 'Escape' && isOpen3D && !isAnimating3D) toggleJournal3D();
        });

        // Auto-open 3D journal if query param is set
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('open') === 'true' || urlParams.get('open_journal') === 'true') {
            setTimeout(() => {
                if (!isOpen3D && !isAnimating3D) toggleJournal3D();
            }, 600);
        }

        // Auto-populate custom title from query parameters if present
        const customTitle = urlParams.get('title') || urlParams.get('collection') || urlParams.get('collection_name');
        if (customTitle) {
            const titleEl = document.querySelector('.topbar-title');
            if (titleEl) {
                titleEl.textContent = customTitle;
            }
        }
    });

    // --- Journal Writing Areas ---
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
            if (saved) {
                area.innerHTML = saved;
                rebindImageBlocks(area);
            }

            const isEmpty = () => area.textContent.trim() === '';
            const syncPh = () => { ph.style.display = isEmpty() ? '' : 'none'; };
            area.addEventListener('input', () => {
                syncPh();
                localStorage.setItem('journal-page-' + id, area.innerHTML);
            });
            area.addEventListener('focus', () => {
                activeWritingArea = area;
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
                        activeWritingArea = null;
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
                        activeWritingArea = null;
                    }
                }
            });
        });
    })();

    // --- Toolbar Editor Helper Functions ---
    function isWritingAreaVisible(area) {
        if (!isOpen3D) return false;
        const page = area.closest('.page');
        if (!page || !page.classList.contains('active-page')) return false;
        const isBack = area.closest('.page-back') !== null;
        const isFlipped = page.classList.contains('flipped');
        return isBack === isFlipped;
    }

    function getVisibleWritingArea() {
        if (activeWritingArea && isWritingAreaVisible(activeWritingArea)) {
            return activeWritingArea;
        }
        
        const activePages = Array.from(document.querySelectorAll('.journal-spotlight .page.active-page'));
        const focused = document.activeElement;
        if (focused && focused.classList.contains('page-writing-area') && isWritingAreaVisible(focused)) {
            activeWritingArea = focused;
            return focused;
        }
        
        const nextToFlip = activePages.find(p => !p.classList.contains('flipped'));
        if (nextToFlip) {
            return nextToFlip.querySelector('.page-front .page-writing-area');
        }
        const lastFlipped = activePages.find(p => p.classList.contains('flipped'));
        if (lastFlipped) {
            return lastFlipped.querySelector('.page-back .page-writing-area');
        }
        return null;
    }

    // --- Toolbar Editor Script ---
    const FORMAT_CMDS = ['bold', 'italic', 'underline', 'justifyLeft', 'justifyCenter', 'justifyRight'];

    function updateToolbarFormatStates() {
        if (!isOpen3D) return;
        const toolbar = document.getElementById('journalEditorToolbar');
        if (!toolbar) return;

        toolbar.querySelectorAll('[data-cmd]').forEach(btn => {
            const cmd = btn.dataset.cmd;
            if (!FORMAT_CMDS.includes(cmd)) return;
            let active = false;
            try {
                active = document.queryCommandState(cmd);
            } catch (_) { /* ignore when no selection */ }
            btn.classList.toggle('is-active', active);
        });

        // Update font size select state if active selection has a size
        const fontSizeSelect = document.getElementById('tb-font-size');
        if (fontSizeSelect) {
            try {
                const size = document.queryCommandValue('fontSize');
                if (size && ['2', '3', '4', '5', '6'].includes(size)) {
                    fontSizeSelect.value = size;
                }
            } catch (_) {}
        }
    }

    document.addEventListener('selectionchange', updateToolbarFormatStates);

    const toolbarEl = document.getElementById('journalEditorToolbar');
    if (toolbarEl) {
        toolbarEl.querySelectorAll('[data-cmd]').forEach(btn => {
            btn.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Keep focus and selection on contenteditable area
                const targetArea = getVisibleWritingArea();
                if (!targetArea) return;
                
                targetArea.focus();
                const cmd = btn.dataset.cmd;
                document.execCommand(cmd, false, null);
                targetArea.dispatchEvent(new Event('input'));
                requestAnimationFrame(updateToolbarFormatStates);
            });
        });

        const fontSizeSelect = document.getElementById('tb-font-size');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', () => {
                const targetArea = getVisibleWritingArea();
                if (!targetArea) return;
                targetArea.focus();
                document.execCommand('fontSize', false, fontSizeSelect.value);
                targetArea.dispatchEvent(new Event('input'));
            });
        }
    }

    const imgBtn = document.getElementById('tb-img-btn');
    const imgInput = document.getElementById('tb-img-input');

    if (imgBtn && imgInput) {
        imgBtn.addEventListener('click', (e) => {
            e.preventDefault();
            imgInput.click();
        });

        imgInput.addEventListener('change', () => {
            const file = imgInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload_media', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.url) {
                    insertImageAtCursor(data.url);
                } else {
                    alert('Upload failed: ' + (data.error || 'unknown error'));
                }
                imgInput.value = '';
            })
            .catch(err => {
                console.error('Error uploading image:', err);
                alert('Upload failed: ' + err.message);
                imgInput.value = '';
            });
        });
    }

    function rebindImageBlocks(area) {
        area.querySelectorAll('.img-block').forEach(wrapper => {
            const img = wrapper.querySelector('img');
            const handle = wrapper.querySelector('.img-resize-handle');
            const deleteBtn = wrapper.querySelector('.img-delete-btn');
            
            // Check or create alignment bar if not present or incomplete in legacy markup
            let alignBar = wrapper.querySelector('.img-align-bar');
            if (!alignBar || !alignBar.querySelector('[data-align="free"]')) {
                if (alignBar) alignBar.remove();
                
                alignBar = document.createElement('div');
                alignBar.className = 'img-align-bar';
                alignBar.innerHTML = `
                    <button class="align-btn" data-align="left" title="Wrap Left"><i class="fas fa-align-left"></i></button>
                    <button class="align-btn" data-align="center" title="Inline Center"><i class="fas fa-align-center"></i></button>
                    <button class="align-btn" data-align="right" title="Wrap Right"><i class="fas fa-align-right"></i></button>
                    <button class="align-btn" data-align="free" title="Free Move"><i class="fas fa-arrows-alt"></i></button>
                `;
                wrapper.appendChild(alignBar);
            }

            if (img && handle && deleteBtn) {
                makeImageInteractive(wrapper, img, handle, deleteBtn);
            }
        });
    }

    function insertImageAtCursor(url) {
        activeWritingArea = getVisibleWritingArea();
        if (!activeWritingArea) return;
        activeWritingArea.focus();

        const wrapper = document.createElement('div');
        wrapper.className = 'img-block';
        wrapper.contentEditable = 'false';
        
        // Default style is floated left with text wrapping
        wrapper.style.float = 'left';
        wrapper.style.display = 'inline-block';
        wrapper.style.margin = '8px 16px 8px 0';
        wrapper.style.position = 'relative';

        const img = document.createElement('img');
        img.src = url;
        img.style.width = '160px';

        const handle = document.createElement('div');
        handle.className = 'img-resize-handle';

        const deleteBtn = document.createElement('div');
        deleteBtn.className = 'img-delete-btn';
        deleteBtn.innerHTML = '&times;';

        const alignBar = document.createElement('div');
        alignBar.className = 'img-align-bar';
        alignBar.innerHTML = `
            <button class="align-btn active" data-align="left" title="Wrap Left"><i class="fas fa-align-left"></i></button>
            <button class="align-btn" data-align="center" title="Inline Center"><i class="fas fa-align-center"></i></button>
            <button class="align-btn" data-align="right" title="Wrap Right"><i class="fas fa-align-right"></i></button>
            <button class="align-btn" data-align="free" title="Free Move"><i class="fas fa-arrows-alt"></i></button>
        `;

        wrapper.appendChild(img);
        wrapper.appendChild(handle);
        wrapper.appendChild(deleteBtn);
        wrapper.appendChild(alignBar);

        makeImageInteractive(wrapper, img, handle, deleteBtn);

        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            if (activeWritingArea.contains(range.commonAncestorContainer)) {
                range.deleteContents();
                range.insertNode(wrapper);
                
                // Collapse caret range after inserted image to continue writing
                const afterRange = document.createRange();
                afterRange.setStartAfter(wrapper);
                afterRange.collapse(true);
                selection.removeAllRanges();
                selection.addRange(afterRange);
            } else {
                activeWritingArea.appendChild(wrapper);
            }
        } else {
            activeWritingArea.appendChild(wrapper);
        }

        activeWritingArea.dispatchEvent(new Event('input'));
    }

    function makeImageInteractive(wrapper, img, handle, deleteBtn) {
        // Prevent selection loss when clicking wrapper
        wrapper.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
        });

        // Set active state on alignment button initially matching styles
        const alignBar = wrapper.querySelector('.img-align-bar');
        if (alignBar) {
            const currentAlign = wrapper.style.position === 'absolute' ? 'free' : (wrapper.style.float === 'left' ? 'left' : (wrapper.style.float === 'right' ? 'right' : 'center'));
            alignBar.querySelectorAll('.align-btn').forEach(btn => {
                if (btn.dataset.align === currentAlign) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            // Bind click handlers for alignment options
            alignBar.querySelectorAll('.align-btn').forEach(btn => {
                btn.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    const align = btn.dataset.align;
                    alignBar.querySelectorAll('.align-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    if (align === 'free') {
                        // Convert to absolute positioning for free layout
                        const rect = wrapper.getBoundingClientRect();
                        const parent = wrapper.parentElement;
                        const parentRect = parent.getBoundingClientRect();
                        
                        wrapper.style.position = 'absolute';
                        wrapper.style.left = (rect.left - parentRect.left) + 'px';
                        wrapper.style.top = (rect.top - parentRect.top) + 'px';
                        wrapper.style.float = 'none';
                        wrapper.style.display = 'inline-block';
                        wrapper.style.margin = '0';
                        wrapper.style.clear = 'none';
                    } else {
                        // Convert to relative positioning for normal document flow
                        wrapper.style.position = 'relative';
                        wrapper.style.left = '';
                        wrapper.style.top = '';
                        
                        if (align === 'left') {
                            wrapper.style.float = 'left';
                            wrapper.style.display = 'inline-block';
                            wrapper.style.margin = '8px 16px 8px 0';
                            wrapper.style.clear = 'none';
                        } else if (align === 'center') {
                            wrapper.style.float = 'none';
                            wrapper.style.display = 'block';
                            wrapper.style.margin = '12px auto';
                            wrapper.style.clear = 'both';
                        } else if (align === 'right') {
                            wrapper.style.float = 'right';
                            wrapper.style.display = 'inline-block';
                            wrapper.style.margin = '8px 0 8px 16px';
                            wrapper.style.clear = 'none';
                        }
                    }

                    const area = wrapper.closest('.page-writing-area');
                    if (area) area.dispatchEvent(new Event('input'));
                });
            });
        }

        let isDragging = false;
        let startX = 0;
        let startY = 0;
        let placeholder = null;

        wrapper.addEventListener('pointerdown', (e) => {
            if (e.button !== 0) return; // Only left-click drag
            if (e.target.closest('.img-resize-handle') || e.target.closest('.img-delete-btn') || e.target.closest('.img-align-bar')) {
                return;
            }

            e.stopPropagation();

            // Toggle selection class
            document.querySelectorAll('.img-block.selected').forEach(el => el.classList.remove('selected'));
            wrapper.classList.add('selected');

            startX = e.clientX;
            startY = e.clientY;
            isDragging = false;

            const rect = wrapper.getBoundingClientRect();
            const pointerOffsetX = e.clientX - rect.left;
            const pointerOffsetY = e.clientY - rect.top;

            let currentParent = wrapper.closest('.page-writing-area');
            if (!currentParent) return;

            // Cache rects of active visible writing areas
            const visibleAreas = [];
            document.querySelectorAll('.page-writing-area').forEach(area => {
                if (isWritingAreaVisible(area)) {
                    visibleAreas.push({
                        element: area,
                        rect: area.getBoundingClientRect(),
                        width: area.clientWidth,
                        height: area.clientHeight
                    });
                }
            });

            const initialAreaInfo = visibleAreas.find(info => info.element === currentParent);
            let currentParentRect = initialAreaInfo ? initialAreaInfo.rect : currentParent.getBoundingClientRect();
            let currentParentWidth = initialAreaInfo ? initialAreaInfo.width : currentParent.clientWidth;
            let currentParentHeight = initialAreaInfo ? initialAreaInfo.height : currentParent.clientHeight;

            const wrapperWidth = wrapper.offsetWidth;
            const wrapperHeight = wrapper.offsetHeight;

            // Determine if we are dragging absolutely or inline
            const isFreeMode = wrapper.style.position === 'absolute';

            let initialLeft = parseFloat(wrapper.style.left) || 0;
            let initialTop = parseFloat(wrapper.style.top) || 0;
            let dx = 0;
            let dy = 0;

            const onPointerMove = (moveEvent) => {
                const deltaX = moveEvent.clientX - startX;
                const deltaY = moveEvent.clientY - startY;

                if (!isDragging && (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5)) {
                    isDragging = true;
                    wrapper.classList.add('dragging');
                    window.draggedImgBlock = wrapper;

                    if (!isFreeMode) {
                        // WRAP MODE: Insert DOM layout placeholder
                        placeholder = document.createElement('div');
                        placeholder.className = 'img-block-placeholder';
                        placeholder.style.width = wrapper.offsetWidth + 'px';
                        placeholder.style.height = wrapper.offsetHeight + 'px';
                        placeholder.style.display = window.getComputedStyle(wrapper).display;
                        placeholder.style.float = window.getComputedStyle(wrapper).float;
                        placeholder.style.margin = window.getComputedStyle(wrapper).margin;
                        placeholder.style.border = '2px dashed #8A9A70';
                        placeholder.style.borderRadius = '8px';
                        placeholder.style.boxSizing = 'border-box';

                        wrapper.parentNode.insertBefore(placeholder, wrapper);
                        wrapper.style.position = 'fixed';
                        wrapper.style.zIndex = '1000';
                        wrapper.style.pointerEvents = 'none';
                        wrapper.style.opacity = '0.7';
                    } else {
                        // FREE MODE: Set transform baseline
                        wrapper.style.transform = 'translate3d(0, 0, 0)';
                    }
                }

                if (isDragging) {
                    if (!isFreeMode) {
                        // WRAP MODE positioning
                        wrapper.style.left = (moveEvent.clientX - pointerOffsetX) + 'px';
                        wrapper.style.top = (moveEvent.clientY - pointerOffsetY) + 'px';

                        // Find target area under cursor
                        let targetArea = null;
                        for (const areaInfo of visibleAreas) {
                            const r = areaInfo.rect;
                            if (moveEvent.clientX >= r.left && moveEvent.clientX <= r.right &&
                                moveEvent.clientY >= r.top && moveEvent.clientY <= r.bottom) {
                                targetArea = areaInfo.element;
                                break;
                            }
                        }

                        if (targetArea) {
                            let range = null;
                            if (document.caretRangeFromPoint) {
                                range = document.caretRangeFromPoint(moveEvent.clientX, moveEvent.clientY);
                            } else if (document.caretPositionFromPoint) {
                                const pos = document.caretPositionFromPoint(moveEvent.clientX, moveEvent.clientY);
                                if (pos) {
                                    range = document.createRange();
                                    range.setStart(pos.offsetNode, pos.offset);
                                    range.setEnd(pos.offsetNode, pos.offset);
                                }
                            }

                            if (range && targetArea.contains(range.startContainer)) {
                                const targetNode = range.startContainer;
                                if (!wrapper.contains(targetNode) && !placeholder.contains(targetNode)) {
                                    range.insertNode(placeholder);
                                }
                            } else {
                                // Empty area drag: append placeholder to end
                                if (placeholder.parentNode !== targetArea) {
                                    targetArea.appendChild(placeholder);
                                }
                            }
                        }
                    } else {
                        // FREE MODE positioning
                        let targetArea = null;
                        let targetRect = null;
                        let targetWidth = 0;
                        let targetHeight = 0;

                        for (const areaInfo of visibleAreas) {
                            const r = areaInfo.rect;
                            if (moveEvent.clientX >= r.left && moveEvent.clientX <= r.right &&
                                moveEvent.clientY >= r.top && moveEvent.clientY <= r.bottom) {
                                targetArea = areaInfo.element;
                                targetRect = r;
                                targetWidth = areaInfo.width;
                                targetHeight = areaInfo.height;
                                break;
                            }
                        }

                        // Handle page crossing in free mode
                        if (targetArea && wrapper.parentElement !== targetArea) {
                            const currentViewportLeft = moveEvent.clientX - pointerOffsetX;
                            const currentViewportTop = moveEvent.clientY - pointerOffsetY;

                            targetArea.appendChild(wrapper);
                            currentParent = targetArea;
                            currentParentRect = targetRect;
                            currentParentWidth = targetWidth;
                            currentParentHeight = targetHeight;

                            initialLeft = currentViewportLeft - currentParentRect.left;
                            initialTop = currentViewportTop - currentParentRect.top;

                            startX = moveEvent.clientX;
                            startY = moveEvent.clientY;
                            wrapper.style.left = initialLeft + 'px';
                            wrapper.style.top = initialTop + 'px';
                            wrapper.style.transform = 'translate3d(0, 0, 0)';
                            return;
                        }

                        if (currentParent) {
                            let newLeft = initialLeft + deltaX;
                            let newTop = initialTop + deltaY;

                            const maxLeft = currentParentWidth - wrapperWidth;
                            const maxTop = currentParentHeight - wrapperHeight;

                            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                            newTop = Math.max(0, Math.min(newTop, maxTop));

                            dx = newLeft - initialLeft;
                            dy = newTop - initialTop;

                            wrapper.style.transform = `translate3d(${dx}px, ${dy}px, 0)`;
                        }
                    }
                }
            };

            const onPointerUp = () => {
                document.removeEventListener('pointermove', onPointerMove);
                document.removeEventListener('pointerup', onPointerUp);

                if (isDragging) {
                    wrapper.classList.remove('dragging');
                    window.draggedImgBlock = null;

                    if (!isFreeMode) {
                        // Restore wrap styles
                        wrapper.style.position = 'relative';
                        wrapper.style.left = '';
                        wrapper.style.top = '';
                        wrapper.style.zIndex = '';
                        wrapper.style.pointerEvents = '';
                        wrapper.style.opacity = '';

                        if (placeholder && placeholder.parentNode) {
                            placeholder.parentNode.replaceChild(wrapper, placeholder);
                        }
                        placeholder = null;
                    } else {
                        // Commit absolute coordinates
                        const finalLeft = initialLeft + dx;
                        const finalTop = initialTop + dy;
                        wrapper.style.left = finalLeft + 'px';
                        wrapper.style.top = finalTop + 'px';
                        wrapper.style.transform = 'none';
                    }

                    document.querySelectorAll('.page-writing-area').forEach(area => {
                        area.dispatchEvent(new Event('input'));
                    });
                }
            };

            document.addEventListener('pointermove', onPointerMove);
            document.addEventListener('pointerup', onPointerUp);
        });

        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                wrapper.classList.remove('selected');
            }
        });

        deleteBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            wrapper.remove();
            if (activeWritingArea) activeWritingArea.dispatchEvent(new Event('input'));
        });

        handle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const startX = e.clientX;
            const startWidth = img.offsetWidth;

            const onMove = (e) => {
                const newWidth = Math.max(60, startWidth + (e.clientX - startX));
                img.style.width = newWidth + 'px';
            };

            const onUp = () => {
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);

                if (activeWritingArea) activeWritingArea.dispatchEvent(new Event('input'));
            };

            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        });
    }

    // ── Save Entry + Envelope ──
    let envOpened = false;
    let shouldFlipAfterEnvelope = false;

    function saveEntryAndShowEnvelope() {
        const areas = document.querySelectorAll('.page-writing-area');
        let fullText = '';
        areas.forEach(area => {
            const text = area.innerText.trim();
            if (text) fullText += text + '\n\n';
        });

        if (!fullText.trim()) {
            alert('Write something first before saving.');
            return;
        }

        const statusInd = document.getElementById('save-status');
        if (statusInd) statusInd.textContent = 'SAVING...';

        fetch('/save_entry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: fullText.trim() })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (statusInd) statusInd.textContent = 'SAVED';
                if (window.parent) {
                    window.parent.postMessage('journal_saved', '*');
                }
                shouldFlipAfterEnvelope = true;
                const letter = data.letter || 'Thank you for writing today.';
                showEnvelope(letter);
                areas.forEach(area => {
                    area.innerHTML = '';
                    area.dispatchEvent(new Event('input'));
                    const pageId = area.dataset.pageId;
                    if (pageId) localStorage.removeItem('journal-page-' + pageId);
                });
            } else {
                if (statusInd) statusInd.textContent = 'SAVED';
                alert('Could not save: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(err => {
            if (statusInd) statusInd.textContent = 'SAVED';
            alert('Save failed: ' + err.message);
        });
    }

    function showEnvelope(letterText) {
        // Build preview (first line) and full paragraphs
        const paragraphs = letterText.split('\n\n').filter(p => p.trim());
        const preview = paragraphs[1] ? paragraphs[1].substring(0, 80) + '...' : letterText.substring(0, 80) + '...';
        const title = paragraphs[0] || 'Dear friend,';

        document.getElementById('envLetterPreview').textContent = preview;
        document.getElementById('envModalTitle').textContent = title;

        const modalBody = document.getElementById('envModalBody');
        modalBody.innerHTML = '';
        paragraphs.slice(1).forEach(para => {
            const p = document.createElement('p');
            p.textContent = para;
            modalBody.appendChild(p);
        });

        // Reset envelope state
        envOpened = false;
        document.getElementById('envFlap').classList.remove('open');
        document.getElementById('envFlapBack').classList.remove('open');
        const perspective = document.querySelector('.env-flap-perspective');
        if (perspective) perspective.classList.remove('open');
        document.getElementById('envFlapShadow').classList.remove('show');
        document.getElementById('envSeal').classList.remove('gone');
        document.getElementById('envLetter').classList.remove('show', 'rise');
        document.getElementById('envHint').classList.remove('hidden');

        document.getElementById('envOverlay').classList.add('show');
    }

    function openEnvelope() {
        if (envOpened) return;
        envOpened = true;

        document.getElementById('envHint').classList.add('hidden');
        document.getElementById('envSeal').classList.add('gone');

        setTimeout(() => {
            document.getElementById('envFlapShadow').classList.add('show');
        }, 200);

        setTimeout(() => {
            document.getElementById('envFlap').classList.add('open');
            document.getElementById('envFlapBack').classList.add('open');
            const p = document.querySelector('.env-flap-perspective');
            if (p) p.classList.add('open');
        }, 350);

        setTimeout(() => {
            document.getElementById('envFlapShadow').classList.remove('show');
        }, 1100);

        setTimeout(() => {
            const l = document.getElementById('envLetter');
            l.classList.add('show');
            setTimeout(() => l.classList.add('rise'), 80);
        }, 1050);
    }

    function expandLetter() {
        document.getElementById('envModalOverlay').classList.add('show');
    }

    function closeEnvelopeWithAnimation() {
        const overlay = document.getElementById('envOverlay');
        const letter = document.getElementById('envLetter');
        const flap = document.getElementById('envFlap');
        const flapBack = document.getElementById('envFlapBack');
        const flapPerspective = document.querySelector('.env-flap-perspective');
        const seal = document.getElementById('envSeal');
        const flapShadow = document.getElementById('envFlapShadow');

        const doFlip = shouldFlipAfterEnvelope;
        shouldFlipAfterEnvelope = false;

        if (envOpened) {
            // Reverse: lower letter → close flap → restore seal → fade overlay
            letter.classList.remove('rise');
            setTimeout(() => letter.classList.remove('show'), 600);

            setTimeout(() => flapShadow.classList.add('show'), 700);
            setTimeout(() => {
                flap.classList.remove('open');
                flapBack.classList.remove('open');
                if (flapPerspective) flapPerspective.classList.remove('open');
            }, 900);
            setTimeout(() => {
                flapShadow.classList.remove('show');
                seal.classList.remove('gone');
            }, 2000);
            setTimeout(() => {
                overlay.classList.remove('show');
                if (doFlip) setTimeout(() => autoFlipPage(), 350);
            }, 2400);
        } else {
            overlay.classList.remove('show');
            if (doFlip) setTimeout(() => autoFlipPage(), 400);
        }
    }

    function autoFlipPage() {
        if (!isOpen3D) return;
        const nextToFlip = Array.from(allPages).find(p => !p.classList.contains('flipped'));
        if (nextToFlip) {
            nextToFlip.classList.add('flipped');
            updateZIndices();
            activeWritingArea = null;
        }
    }

    function closeEnvelope() {
        closeEnvelopeWithAnimation();
    }

    function closeLetterModal(e) {
        const overlay = document.getElementById('envModalOverlay');
        if (e.target === overlay || e.target.classList.contains('env-modal-close')) {
            overlay.classList.remove('show');
            setTimeout(() => closeEnvelopeWithAnimation(), 300);
        }
    }

    // --- Topbar Custom Action Listeners ---
    window.handleTopbarBack = function(e) {
        e.preventDefault();
        if (window.self !== window.top) {
            // Embedded inside an iframe (Sanctuary modal room)
            window.parent.postMessage('close_journal_overlay', '*');
        } else {
            // Standalone web page
            window.location.href = "/archive";
        }
    };

    window.setEditorMode = function(mode) {
        const areas = document.querySelectorAll('.page-writing-area');
        const btnEdit = document.getElementById('btn-mode-edit');
        const btnPreview = document.getElementById('btn-mode-preview');

        if (mode === 'preview') {
            areas.forEach(area => area.setAttribute('contenteditable', 'false'));
            if (btnEdit) btnEdit.classList.remove('active');
            if (btnPreview) btnPreview.classList.add('active');
        } else {
            areas.forEach(area => area.setAttribute('contenteditable', 'true'));
            if (btnEdit) btnEdit.classList.add('active');
            if (btnPreview) btnPreview.classList.remove('active');
        }
    };

    // --- Dynamic Zoom Control ---
    window.zoomJournal = function(factor) {
        function getBaseScale() {
            const h = window.innerHeight;
            const w = window.innerWidth;
            if (h < 600 || w < 520) return 0.62;
            if (h < 720 || w < 768) return 0.80;
            if (h < 850 || w < 900) return 0.95;
            return 1.15;
        }

        if (factor === 1.0) {
            window.currentScale = null;
            document.documentElement.style.removeProperty('--journal-scale');
        } else {
            if (!window.currentScale) {
                window.currentScale = getBaseScale();
            }
            window.currentScale = Math.max(0.35, Math.min(2.0, window.currentScale * factor));
            document.documentElement.style.setProperty('--journal-scale', window.currentScale);
        }
    };
