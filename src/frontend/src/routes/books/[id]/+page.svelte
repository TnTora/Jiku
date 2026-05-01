<script lang="ts">
    import { onMount } from "svelte";
    import { setEbookReaderOptionsContext } from "./context";
	import TopBar from "./TopBar.svelte";
    import OptionPanel from "./OptionPanel.svelte";
    import SidePanel from "./SidePanel.svelte";

    let { data } = $props();
    let { book, content } = data;
    // let vertical = $state(false);
    // let paginated = $state(true);
    console.log(book);

    let options = $state({
        font_size: 20,
        line_height: 40,
        vertical: true,
        paginated: true,
        show_progress: true,
        limit_progress_to_section: true,
    });

    setEbookReaderOptionsContext(options);

    let show_options = $state(false);
    let show_side_panel = $state(false);

    let book_container: HTMLDivElement;
    let book_container_offHeight: number = $state(0);
    let book_container_offWidth: number = $state(0);


    let book_container_scrollPercent: number = $state(0);

    let book_container_inline_offset: number = $derived(
        options.vertical? book_container_offHeight:
        book_container_offWidth
    );

    let book_container_block_offset: number = $derived(
        options.vertical? book_container_offWidth:
        book_container_offHeight
    );

    
    let page_top_par: HTMLParagraphElement | null;
    let skip_intersection: boolean = false;


    let pageScrollParam = $derived(
        options.vertical? (top:number) => { return {top: top} } :
        (left:number) => { return {left: left} }
    );


    let getInlineOffset = $derived(
        options.vertical? (el: HTMLElement) => { return el.offsetTop } :
        (el: HTMLElement) => { return el.offsetLeft }
    );

    let getBlockOffset = $derived(
        options.vertical? (el: HTMLElement) => { return el.offsetLeft } :
        (el: HTMLElement) => { return el.offsetTop }
    );


    function jumpTo(scroll_position: number) {
        book_container.scrollTo(
            pageScrollParam(Math.floor(scroll_position / book_container_inline_offset) * book_container_inline_offset)
        );
    }


    function nextPage(){
        skip_intersection = false;
        book_container.scrollBy(pageScrollParam(book_container_inline_offset));
    }

    function prevPage(){
        skip_intersection = false;
        book_container.scrollBy(pageScrollParam(-book_container_inline_offset));
    }


    let intersection_observer: IntersectionObserver;
    let resize_observer: ResizeObserver;

    function observeFirstColElements_paginated(){
        const elements = book_container.querySelectorAll("p[data-char-start]") as NodeListOf<HTMLParagraphElement>;
        let previous_offset: number = 0;
        let page: number = 0;

        elements.forEach(el => {
            const first_tok = el.querySelector("span[data-tok]");

            if (!first_tok) { return };

            const curr_offset = getInlineOffset(first_tok as HTMLElement);
            // console.log(el, curr_offset);

            if (curr_offset >= previous_offset) {
                // console.log(el);
                intersection_observer.observe(el);
                page++;
                previous_offset = page * book_container_inline_offset;
            }
        });

        // console.log(intersection_observer);
    }

    function observeFirstColElements_scroll(){
        const elements = book_container.querySelectorAll("p[data-char-start]") as NodeListOf<HTMLParagraphElement>;
        let previous_offset: number = 0;
        let page: number = 0;

        elements.forEach(el => {
            const first_tok = el.querySelector("span[data-tok]");

            if (!first_tok) { return };

            const curr_offset = Math.abs(getBlockOffset(first_tok as HTMLElement));
            // console.log("scroll", el, curr_offset);

            if (curr_offset >= previous_offset) {
                // console.log("scroll", el);
                intersection_observer.observe(el);
                page++;
                previous_offset = page * book_container_block_offset;
            }
        });

        // console.log(intersection_observer);
    }

    

    let observeFirstColElements = $derived(
        options.paginated? observeFirstColElements_paginated:
        options.show_progress? observeFirstColElements_scroll:
        () => {}
    )

    onMount(() => {
        page_top_par = null;

        intersection_observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !skip_intersection) {
                    page_top_par = entry.target as HTMLParagraphElement;

                    if (options.paginated) {
                        book_container_scrollPercent = options.vertical?
                            (book_container.scrollTop / book_container.scrollHeight) * 100:
                            (book_container.scrollLeft / book_container.scrollWidth) * 100;
                    } else {
                        book_container_scrollPercent = options.vertical?
                            (-book_container.scrollLeft / book_container.scrollWidth) * 100:
                            (book_container.scrollTop / book_container.scrollHeight) * 100;
                    }

                    // console.log(page_top_par);
                }
            })
        }, {});
    
        let resize_timeout;
        resize_observer = new ResizeObserver(entries => {
            intersection_observer.disconnect();
            if (page_top_par) {
                // console.log("jumping to ", page_top_par);
                jumpTo(getInlineOffset(page_top_par));
            }
            clearTimeout(resize_timeout);
            resize_timeout = setTimeout(() => {
                skip_intersection = true;
                observeFirstColElements();

                if (!options.paginated) {
                    function activateObserver() {
                        skip_intersection = false;
                        book_container.removeEventListener("scroll", activateObserver)
                    };

                    book_container.addEventListener("scroll", activateObserver);
                }
            }, 100);
        });

        resize_observer.observe(book_container);
        // intersection_observer.observe(page_top_par);
        setTimeout(observeFirstColElements, 1000);
        // setInterval(() => {console.log(intersection_observer)}, 2000);
    });


</script>

<svelte:head>
    {#each book.stylesheets as sheet_file}
        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/static/books/{book.id}/stylesheets/{sheet_file}" disabled>
    {/each}
</svelte:head>


<TopBar title={book.metadata.title} toggleOptions={() => {show_options = !show_options}} toggleSidePanel={() => {show_side_panel = !show_side_panel}}/>

{#if show_options}
    <OptionPanel onoutsideclick={() => { show_options = false }} />
{/if}

{#if show_side_panel}
    <SidePanel {book} onoutsideclick={() => { show_side_panel = false }} />
{/if}


{#if options.paginated}
    <!-- Left Arrow -->
    <button onclick={options.vertical? nextPage : prevPage} aria-label={options.vertical? "Next Page" : "Prev Page"} class="w-12 absolute left-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_right,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="m4 10l9 9l1.4-1.5L7 10l7.4-7.5L13 1z" />
        </svg>
    </button>
    <!-- Right Arrow -->
    <button onclick={options.vertical? prevPage : nextPage} aria-label={options.vertical? "Prev Page" : "Next Page"} class="w-12 absolute right-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_left,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="M7 1L5.6 2.5L13 10l-7.4 7.5L7 19l9-9z" />
        </svg>
    </button>
{/if}



<div bind:this={book_container} 
    bind:offsetHeight={book_container_offHeight}
    bind:offsetWidth={book_container_offWidth}
    class="jiku-book-container {options.vertical? "vert-rl" : "horz-tb!"} {options.paginated? "paginated overflow-hidden": "px-12 py-12 overflow-scroll!"} h-screen w-[calc(100vw-2*var(--book-x-margin))]! pt-14 pb-12 bg-neutral-800!" 
    style="{options.paginated? "--book-x-margin: 2rem;" : ""} line-height: {options.line_height}px; font-size: {options.font_size}px"
>
    {@html content}
</div>



<div class="h-8 w-full fixed bottom-0 z-10">
    {#if options.show_progress}
        <div class="h-2 bg-mist-700 absolute bottom-0 {options.vertical? "right-0 rounded-l-full": "left-0 rounded-r-full"} transition-[width] duration-200" style="width:{book_container_scrollPercent}%"></div>
    {/if}
</div>

<style>
    :root {
        --book-x-margin: 0rem;
    }

    .paginated:not(.vert-rl) {
        --custom-gap: 3rem;
        column-gap: var(--custom-gap);
        column-width: calc(50vw - var(--book-x-margin) - var(--custom-gap));
        padding-inline: calc(var(--custom-gap) / 2);
    }

    .paginated.vert-rl {
        --custom-gap: 7rem;
        column-gap: var(--custom-gap);
        column-width: calc(100vh - var(--custom-gap));
        padding-inline: calc(var(--custom-gap) / 2);
    }

    .paginated {
        margin-left: var(--book-x-margin);
        margin-right: var(--book-x-margin);
    }


</style>
