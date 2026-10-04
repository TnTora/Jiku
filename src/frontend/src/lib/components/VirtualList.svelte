<script lang="ts"  generics="T">
	import { createRafHandler } from '$lib/utils/raf';
	import { onMount, tick, untrack, type Snippet } from 'svelte';
    import type { SvelteHTMLElements } from 'svelte/elements';

    interface VisibleItem {
        item: T,
        original_index: number
    }

    type HTMLDivAttributes = SvelteHTMLElements["div"];

    interface Props extends HTMLDivAttributes {
        items: T[],
        guessed_item_size: number,
        vertical?: boolean,
        buffer?: number,
        start_idx?: number,
        end_idx?: number,
        container?: HTMLDivElement,
        persist_selection?: boolean,
        render_item: Snippet<[T, number]>
    }

    let { 
        items,
        guessed_item_size,
        vertical = false,
        buffer = 5,
        start_idx = $bindable(0),
        end_idx = $bindable(0),
        // eslint-disable-next-line no-useless-assignment
        container = $bindable(),
        persist_selection = false,
        render_item,
        ...rest
    }: Props = $props();

    let list_container: HTMLDivElement;
    let list_container_offheight: number = $state(0);
    let list_container_offwidth: number = $state(0);

    let { list_container_offlength , list_container_ortogonal_offlength} = $derived.by(() => {
        if (vertical) {
            return {
                list_container_offlength: list_container_offwidth,
                list_container_ortogonal_offlength: list_container_offheight,
            }
        } else {
            return {
                list_container_offlength: list_container_offheight,
                list_container_ortogonal_offlength: list_container_offwidth,
            }
        }
    });

    let visible_html_elements: HTMLDivElement[] = $state([]);

    let length_map: (number | undefined)[] = [];
    let seen_items_count = 0;
    // svelte-ignore state_referenced_locally
    let average_item_size = $state(guessed_item_size);
    // let estimated_total_size = $derived(average_item_size*items.length);

    let start: number = $state(0);
    let end: number = $state(0);

    let before_spacing = $state(0);
    let rendered_length = $state(0);
    let after_spacing: number = $derived((items.length-end)*average_item_size);

    let visible_items: VisibleItem[] = $derived.by(() => {
        return items.slice(start, end).map((item, i) => {
            return {item:item, original_index: start+i}
        });
    });

    let getOffsetLength = $derived(
        vertical?
        (el: HTMLElement) => { return el.offsetWidth; }:
        (el: HTMLElement) => { return el.offsetHeight; }
    );

    let getScrollPosition = $derived(
        vertical?
        (el: HTMLElement) => { return -el.scrollLeft; }:
        (el: HTMLElement) => { return el.scrollTop; }
    );

    let getScrollLength = $derived(
        vertical?
        (el: HTMLElement) => { return el.scrollWidth; }:
        (el: HTMLElement) => { return el.scrollHeight; }
    );

    let rafHandler = createRafHandler();
    let old_scroll_position: number;

    // $effect(() => {
    //     $inspect(visible_items);
    //     // $inspect(visible_html_elements);
    //     console.log("before_spacing: ", before_spacing);
    //     console.log(getScrollPosition(list_container));
    // });

    $effect(() => {
        console.log(list_container_offheight, list_container_offwidth);
    });

    $effect(() => {
        // console.log("start", start);
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const sync = { start };
        let new_content_length = 0;
        for (let j = 0; j < visible_html_elements.length; j++) {
            if (!visible_html_elements[j]) { continue; }

            // const item_index = start + j;
            const item_index_data = Number(visible_html_elements[j].dataset.originalIndex);

            if (length_map[item_index_data] === undefined) {
                const item_size = getOffsetLength(visible_html_elements[j]);
                // console.log("item_size", item_size);

                if (!item_size) { continue; }

                length_map[item_index_data] = item_size;
                average_item_size = ((average_item_size*seen_items_count) + item_size) / (seen_items_count + 1);
                seen_items_count++;
                // console.log("seen_items_count", seen_items_count);
                // console.log("estimated_total_size", estimated_total_size);
            }

            new_content_length += length_map[item_index_data];
		}
        rendered_length = new_content_length;
        // $inspect(length_map);
    });

    $effect(() => { refreshVisibles(items, list_container_offlength); });

    $effect(() => {
        if (list_container_ortogonal_offlength || vertical){
            length_map.length = 0;
            average_item_size = guessed_item_size;

            const old_start = untrack(() => start_idx);
            tick().then(() => { scrollToIndex(old_start) });
        }
    });

    // svelte-ignore state_referenced_locally
    let old_items_length = items.length;
    // svelte-ignore state_referenced_locally
    let old_container_offlength = list_container_offlength;

    async function refreshVisibles(items: T[], container_offlength?: number) {
        if (!container_offlength || !visible_html_elements) { return; }

        if (!items) {
            start = 0;
            end = 0;
            return;
        }

        // console.log("old_items_length", old_items_length, "items.length", items.length, "old_container_offlength", old_container_offlength, "container_offlength", container_offlength);

        const needs_refresh = ((items.length < old_items_length) || (container_offlength > old_container_offlength) || (rendered_length < container_offlength));
        old_items_length = items.length;
        old_container_offlength = container_offlength;

        if (!needs_refresh) { return; }

        const scrollPos = getScrollPosition(list_container);

        console.log("scrollPos refresh: ", scrollPos);

		await tick(); 

		let visible_length = before_spacing - scrollPos;

        if (visible_length+rendered_length > container_offlength+average_item_size) {
            return;
        }

		let i = start;

		while (visible_length < container_offlength && i < items.length) {
			let el = visible_html_elements[i - start];

			if (!el) {
				end = i + 1;
				await tick(); // await render of new element
				el = visible_html_elements[i - start];
			}

			visible_length += getOffsetLength(el);
			i += 1;
		}

		end = i;
        end_idx = end;

	}

    async function handle_scroll() {
        let scrollPos = getScrollPosition(list_container);

        // console.log("scrollPos: ", scrollPos);

        // avoid recalculating for small scrolling changes
        if ((old_scroll_position !== undefined) && (Math.abs(scrollPos - old_scroll_position) < guessed_item_size*0.75)) {
            return;
        }

        old_scroll_position = scrollPos;
        const old_start = start;
        const old_spacing = before_spacing;

        // console.log("scrollPos handle_scroll: ", scrollPos);

		let i = 0;
		let y = 0;
        let start_buffer = items.length;
        let y_buffer;
        // let content_length = 0;

        await tick();

        // find first visible item
		while (i < items.length) {
            // use guessed_size insetead of average_size to avoid jitter when
            // scrolling up without a known offset
			const item_height = length_map[i] || guessed_item_size;

			if (y + item_height > scrollPos) {
                start_idx = i;
                start_buffer = i;
                y_buffer = y;
				break;
			}

			y += item_height;
			i++;
		}

        // find last item 
		while (i < items.length) {
            const item_height = length_map[i] || average_item_size;
			y += item_height;
			i++;

			if (y > scrollPos + list_container_offlength) break;
		}

        end_idx = i;

        if (y_buffer === undefined) {
            console.log("overscrolled");
            y_buffer = y;
            // let j = end_idx;
            let content_length = 0;

            while (i > 0) {
                content_length += (length_map[i] || average_item_size);
                y_buffer -= (length_map[i] || guessed_item_size);

                if (content_length < list_container_offlength) { break; }

                i--;
            }
            
            start_buffer = i;

        }

        // apply buffer
        let j = 1;
        while (j <= buffer && start_buffer > 0) {
            start_buffer--;
            y_buffer -= (length_map[start_idx-j] || guessed_item_size);
            j++;
        }

        // let estimated_length = 0;

        // for(let i = start_buffer; i < old_start; i++) {
        //     console.log()
        //     estimated_length += (length_map[i] || guessed_item_size);
        // }

        // update states
        start = start_buffer;
        before_spacing = y_buffer;
        end = Math.min(end_idx+buffer, items.length);


        if (start < old_start) {
            // correct scroll position when scrolling up without a known offset
            // due to rendered items size being different from the estimated one
            let actual_length = 0;
            let estimated_length = old_spacing-before_spacing;

            await tick(); // wait for items rendering

            for(let i = start; i < old_start; i++) {
                if (visible_html_elements[i-start]) {
                    actual_length += getOffsetLength(visible_html_elements[i-start]);
                }
            }

            const d = actual_length - estimated_length;

            if (!d) { return; }

            const target = vertical? 
                {left: - d} :
                {top: d} ;

            // console.log(old_start, start);
            // console.log("before_spacing", before_spacing, "old_spacing", old_spacing);
            // console.log(actual_length, estimated_length, actual_length - estimated_length);
            // console.log("target", target);

            list_container.scrollBy(target);
        }

        // console.log("saved_sel", saved_sel);
        if (persist_selection) {
            const sel = window.getSelection();
            if (saved_sel.text) {
                if ((start <= saved_sel.start_id && saved_sel.start_id < end)  || (start <= saved_sel.end_id && saved_sel.end_id < end)) {
                    await tick();
                    restoreSelection();
                } else {
                    sel?.empty();
                }
            } else if (sel?.rangeCount) {
                sel?.empty();
            }
        }
	}


    export function clearItems() {
        items.splice(0);
        length_map.length = 0;
        average_item_size = guessed_item_size;
    }

    export function deleteItem(index:number) {
        if (index < 0 || index >= items.length) { return; }

        const removed_length = length_map.splice(index, 1)[0];

        if (removed_length !== undefined) {
            average_item_size = ((average_item_size*seen_items_count)-removed_length) / (seen_items_count-1);
            seen_items_count--;
        }

        items.splice(index, 1);
    }

    export async function scrollToIndex(index: number) {
        if (index < 0) {
            index = Math.max(0, items.length + index);
        } else if (index >= items.length) {
            index = items.length - 1;
        }

		let y = 0;

        for (let i=0; i < index; i++) {
            y += length_map[i] || guessed_item_size;
        }

        const target = vertical? {left: -y}: {top: y};
        const scroll_length = getScrollLength(list_container);

        console.log("index", index, "target", target, "scroll_length", scroll_length);

        if ((index < start || index > end) && (scroll_length < y+list_container_offlength)) {
            after_spacing += (y-scroll_length+list_container_offlength);
            await tick();
            console.log(getScrollLength(list_container));
        }

        list_container.scrollTo(target);
	}

    export function updateLengthMap(index: number, value?: number) {
        length_map[index] = value;
        // console.log(`length ${index}: ${value}`);
    }

    function scheduled_scroll() {
        rafHandler(handle_scroll);
    }

    interface SavedSelection {
        start_id: number,
        start_offset: number,
        end_id: number,
        end_offset: number,
        text: string,
    }

    let saved_sel: SavedSelection = {
        start_id: -1,
        start_offset: 0,
        end_id: -1,
        end_offset: 0,
        text: "",
    };

    function saveSelection() {
        let sel = window.getSelection();
        let text_sel = sel?.toString();
        // console.log(text_sel);
        if (!text_sel) { return; }

        let range = sel?.getRangeAt(0);
        // console.log(range);
        if (!range) { return; }

        let start_node: HTMLElement | Node | null = range.startContainer;
        let start_id: number | null = null;

        while (start_node && !start_id) {
            if (start_node.nodeType === 1) {   
                const data_id = (start_node as HTMLElement).getAttribute("data-original-index");
                if (data_id) {
                    start_id = Number(data_id);
                    break;
                }
            }
            start_node = start_node.parentElement;
        }

        // console.log(start_node, start_id);
        if (!start_node || start_id === null) { return; }

        let pre_selection_range = range.cloneRange();
        pre_selection_range.selectNodeContents(start_node);
        pre_selection_range.setEnd(range.startContainer, range.startOffset);
        let start_offset = pre_selection_range.toString().length;



        let end_node: HTMLElement | Node | null = range.endContainer;
        let end_id: number | null = null;

        while (end_node && !end_id) {
            if (end_node.nodeType === 1) {   
                const data_id = (end_node as HTMLElement).getAttribute("data-original-index");
                if (data_id) {
                    end_id = Number(data_id);
                    break;
                }
            }
            end_node = end_node.parentElement;
        }

        // console.log(end_node);
        if (!end_node || end_id === null) { return; }

        let end_selection_range = range.cloneRange();
        end_selection_range.selectNodeContents(end_node);
        end_selection_range.setEnd(range.endContainer, range.endOffset);
        let end_offset = end_selection_range.toString().length;

        return {
            start_id: start_id,
            start_offset: start_offset,
            end_id: end_id,
            end_offset: end_offset,
            text: text_sel,
        };
    };

    function restoreSelection() {
        // console.log("restoring selection ", saved_sel);
        if (!saved_sel.text) { return; }

        let range = document.createRange();
        range.setStart(list_container, 0);
        range.collapse(true);

        let char_index = 0;
        let node, found_start = false;
        let node_stack = [];
        const start_line = document.querySelector(`div[data-original-index='${saved_sel.start_id}'`);
        const end_line = document.querySelector(`div[data-original-index='${saved_sel.end_id}'`);

        // console.log("start_line", start_line);
        // console.log("end_line", end_line);

        if (start_line) {
            node_stack = [start_line];
            while ((node = node_stack.pop())) {
                if (node.nodeType == 3) {
                    let next_char_index = char_index + node.length;
                    if (saved_sel.start_offset >= char_index && saved_sel.start_offset <= next_char_index) {
                        range.setStart(node, saved_sel.start_offset - char_index);
                        found_start = true;
                        if (saved_sel.start_offset < next_char_index) {
                            node_stack.push(node);
                        } else {
                            char_index = next_char_index;
                        }
                        break;
                    }
                    char_index = next_char_index;
                } else {
                    let i = node.childNodes.length;
                    while (i--) {
                        node_stack.push(node.childNodes[i]);
                    }
                }
            }
        }

        if (saved_sel.end_id !== saved_sel.start_id) {
            char_index = 0;
            node_stack = [end_line];
        }

        if (end_line) {
            while ((node = node_stack.pop())) {
                if (node.nodeType == 3) {
                    let next_char_index = char_index + node.length;
                    if (saved_sel.end_offset >= char_index && saved_sel.end_offset <= next_char_index) {
                        range.setEnd(node, saved_sel.end_offset - char_index);
                        break;
                    }
                    char_index = next_char_index;
                } else {
                    let i = node.childNodes.length;
                    while (i--) {
                        node_stack.push(node.childNodes[i]);
                    }
                }
            }
        } else if (found_start) {
            const clone = range.cloneRange()
            range.selectNodeContents(list_container);
            range.setStart(clone.startContainer, clone.startOffset);
        }

        // console.log(range);

        const sel = window.getSelection();
        if (!sel) { return; }
        sel.removeAllRanges();
        sel.addRange(range);
    }

    function clearSelection() {
        // console.log("clearSelection");
        // const sel = window.getSelection();
        // if (!(event.target instanceof Element) || sel?.containsNode(event.target)) { return; }

        if (saved_sel.text) {
            saved_sel.text = "";
            console.log("cleared selection", saved_sel);
        }
    }

    function handleSelection() {
        // console.log("selectionchange");
        const curr_sel = saveSelection();
        // console.log("curr_sel", curr_sel);
        if (curr_sel) {
            saved_sel = curr_sel;
            console.log("saved_sel", saved_sel);
        }
    }

    $effect(() => {
        if (persist_selection) {
            document.addEventListener("selectionchange", handleSelection);
            list_container.addEventListener("mousedown", clearSelection);
        } else {
            document.removeEventListener("selectionchange", handleSelection);
            list_container.removeEventListener("mousedown", clearSelection);
            saved_sel.text = "";
        }
    });

    onMount(() => {
        container = list_container;
        handle_scroll();
    });

</script>

<div
    bind:this={list_container}
    bind:offsetHeight={list_container_offheight}
    bind:offsetWidth={list_container_offwidth}
    onscroll={scheduled_scroll}
    {...rest}
>
    <div style="{vertical? "padding-right": "padding-top"}: {before_spacing}px; {vertical? "padding-left":"padding-bottom"}: {after_spacing}px;">
        {#each visible_items as data, index (data.original_index)}
            <div bind:this={visible_html_elements[index]} data-original-index={data.original_index}>
                {@render render_item(data.item, data.original_index)}
            </div>
       {/each}
    </div>
</div>