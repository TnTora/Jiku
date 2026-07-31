<script lang="ts"  generics="T">
	import { createRafHandler } from '$lib/utils/raf';
	import { onMount, tick, untrack, type Snippet } from 'svelte';
    import { type SvelteHTMLElements } from 'svelte/elements';

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
        container?: HTMLDivElement
        render_item: Snippet<[T, number]>
    }

    let { 
        items,
        guessed_item_size,
        vertical = false,
        buffer = 5,
        start_idx = $bindable(0),
        end_idx = $bindable(0),
        container = $bindable(),
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

    let length_map: number[] = [];
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
        let new_content_length = 0;
        for (let j = 0; j < visible_html_elements.length; j++) {
            if (!visible_html_elements[j]) { continue; }

            if (length_map[start + j] === undefined) {
                const item_size = getOffsetLength(visible_html_elements[j])
                length_map[start + j] = item_size;
                average_item_size = ((average_item_size*seen_items_count) + item_size) / (seen_items_count + 1);
                seen_items_count++;
                // console.log("seen_items_count", seen_items_count);
                // console.log("estimated_total_size", estimated_total_size);
            }

            new_content_length += length_map[start + j];
		}
        rendered_length = new_content_length;
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

    async function refreshVisibles(items: any[], container_offlength?: number) {
        if (!container_offlength || !visible_html_elements) { return; }

        if (!items) {
            start = 0;
            end = 0;
            return;
        }

        const scrollPos = getScrollPosition(list_container);

        // console.log("scrollTop refresh: ", scrollPos);

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

        // update states
        start = start_buffer;
        before_spacing = y_buffer;
        end = Math.min(end_idx+buffer, items.length);

        await tick(); // wait for items rendering

        if (start < old_start) {
            // correct scroll position when scrolling up without a known offset
            // due to rendered items size being different from the estimated one
            let actual_length = 0;
            let estimated_length = old_spacing-before_spacing;

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

    function scheduled_scroll() {
        rafHandler(handle_scroll);
    }

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
        {#each visible_items as data, index}
            <div bind:this={visible_html_elements[index]} data-original-index={data.original_index}>
                {@render render_item(data.item, data.original_index)}
            </div>
       {/each}
    </div>
</div>