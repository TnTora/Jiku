<script lang="ts">
    import { onMount } from "svelte";
    import { setEbookReaderOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
	import TopBar from "./TopBar.svelte";
    import OptionPanel from "./OptionPanel.svelte";
    import SidePanel from "./SidePanel.svelte";

    let { data } = $props();
    let { book, content } = data;
    let curr_section: string = $state("p-003");
    let prev_section: string | null = $derived(
        (book.sections[curr_section].number > 0)? book.spine[book.sections[curr_section].number-1]:
        null
    );
    let next_section: string | null = $derived(
        ((book.sections[curr_section].number >= 0) && (book.sections[curr_section].number < book.spine.length-1))?
        book.spine[book.sections[curr_section].number+1]:
        null
    );
    console.log(book);
    console.log(prev_section, next_section);

    let options = $state({
        font_size: 20,
        line_height: 40,
        vertical: true,
        paginated: true,
        show_progress_bar: true,
        show_progress_tokens: true,
        limit_progress_to_section: true,
    });

    setEbookReaderOptionsContext(options);

    let show_options = $state(false);
    let show_side_panel = $state(false);
    let show_jump_to = $state(false);

    let bookmarking = $state(false);
    let show_bookmarking_confirmation = $state(false);
    let bookmark_selection: number | null = null;

    let book_container: HTMLDivElement;
    let book_container_offHeight: number = $state(0);
    let book_container_offWidth: number = $state(0);

    let book_container_inline_offset: number = $derived(
        options.vertical? book_container_offHeight:
        book_container_offWidth
    );

    let book_container_block_offset: number = $derived(
        options.vertical? book_container_offWidth:
        book_container_offHeight
    );

    
    let page_top_par: HTMLParagraphElement | null;
    let curr_token_abs: number = $state(0);
    let curr_token_rel: number = $derived(curr_token_abs - book.sections[curr_section].start_tok);
    let curr_token: number = $derived(options.limit_progress_to_section? curr_token_rel: curr_token_abs);
    let total_tokens: number = $derived(
        (options.limit_progress_to_section && next_section)? book.sections[next_section].start_tok - book.sections[curr_section].start_tok:
        book.stats.total_tokens
    );
    let skip_intersection: boolean = false;

    let book_container_scrollPercent: number = $derived(
        (curr_token/total_tokens)*100
    );


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
        options.show_progress_bar? observeFirstColElements_scroll:
        () => {}
    )

    onMount(() => {
        page_top_par = null;

        intersection_observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !skip_intersection) {
                    page_top_par = entry.target as HTMLParagraphElement;
                    curr_token_abs = Number(entry.target.querySelector("span[data-tok]")?.getAttribute("data-tok"));

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

    function startBookmarking() {
        if (show_bookmarking_confirmation) {return}

        bookmarking = true;

        function handleClick(event: Event) {
            console.log(event);
            const selected_token = (event.target as Element)?.getAttribute("data-tok");
            if (selected_token) {
                console.log("selected", selected_token);
                bookmark_selection = Number(selected_token);
                show_bookmarking_confirmation = true;
            }
            bookmarking = false;
            document.removeEventListener("click", handleClick, true);
        };

        document.addEventListener("click", handleClick, true);
    };


</script>

<svelte:head>
    {#each book.stylesheets as sheet_file}
        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/static/books/{book.id}/stylesheets/{sheet_file}" disabled>
    {/each}
</svelte:head>


<TopBar title={book.metadata.title}
        toggleOptions={() => {show_options = !show_options}}
        toggleSidePanel={() => {show_side_panel = !show_side_panel}}
        toggleJumpBox={() => {show_jump_to = !show_jump_to}}
        toggleBookmarking={startBookmarking}/>

{#if show_options}
    <OptionPanel onoutsideclick={() => { show_options = false }} />
{/if}

{#if show_side_panel}
    <SidePanel {book} onoutsideclick={() => { show_side_panel = false }} />
{/if}

{#if show_jump_to}
    <div use:clickOutside={"button[title='Jump To']"}
        onoutsideclick={() => {show_jump_to = false}}
        class="absolute w-40 top-13 right-3 z-20 bg-[#1B1B1B] border border-neutral-900 rounded-2xl flex flex-col items-center justify-evenly gap-3 py-3"
    >
        <span>Jump To Token</span>
        <input type="number" class="w-25 bg-neutral-800 rounded-md text-center hide-input-spinners">
        <button title="Jump" class="px-3 py-1 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600">Jump</button>
    </div>
{/if}

{#if bookmarking}
    <div class="absolute w-full z-20 text-neutral-400 bottom-6 text-center text-lg">
        Select Bookmark starting position
    </div>
{/if}

{#if show_bookmarking_confirmation}
    <div class="w-full h-full bg-neutral-800/90 absolute flex items-center justify-center">
        <div class="p-4 bg-[#1B1B1B] border border-neutral-900 rounded-2xl flex flex-col text-center items-center justify-center gap-3">
            <p>Choose a name</p>
            <input type="text" defaultvalue="Bookmark {book.bookmarks.length + 1}" class="text-center bg-neutral-800 rounded-md">
            <div class="flex items-center justify-evenly gap-4">
                <button class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600">Ok</button>
                <button class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
                    onclick={() => {
                        show_bookmarking_confirmation = false;
                        bookmark_selection = null;
                    }}>
                    Cancel
                </button>
            </div>
            
        </div>
    </div>
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
    class="jiku-book-container {bookmarking? "bookmarking": ""} {options.vertical? "vert-rl" : "horz-tb!"} {options.paginated? "paginated overflow-hidden": "px-12 py-12 overflow-scroll!"} h-screen w-[calc(100vw-2*var(--book-x-margin))]! pt-14 pb-12 bg-neutral-800!" 
    style="{options.paginated? "--book-x-margin: 2rem;" : ""} line-height: {options.line_height}px; font-size: {options.font_size}px"
>
    {@html content}
</div>



<div class="h-8 w-full fixed bottom-0 z-10">
    {#if options.show_progress_tokens}
        <span class="absolute rounded text-neutral-500 {options.vertical? "left-2": "right-2"}">{curr_token} / {total_tokens}</span>
    {/if}
    {#if options.show_progress_bar}
        <div class="h-2 {options.limit_progress_to_section? "bg-mist-700": "bg-emerald-800"} absolute bottom-0 {options.vertical? "right-0 rounded-l-full": "left-0 rounded-r-full"} transition-[width] duration-200" style="width:{book_container_scrollPercent}%"></div>
    {/if}
</div>

<style>
    :root {
        --book-x-margin: 0rem;
    }

    :global .bookmarking span:hover{
        background-color: rgb(215, 50, 0) !important;
        cursor:crosshair;
        border-radius: 0.5rem;
        border: 1rem;
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
