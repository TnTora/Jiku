<script lang="ts">
    import { onMount } from "svelte";
    import { scale } from "svelte/transition";
	import TopBar from "./TopBar.svelte";

    let { data } = $props();
    let { book, content } = data;
    let vertical = $state(true);
    let paginated = $state(true);
    console.log(book);

    let book_container: HTMLDivElement;
    let book_container_offHeight: number = $state(0);
    let book_container_offWidth: number = $state(0);

    let book_container_scrollPercent: number = $state(0);

    let book_container_offLenght: number = $derived(
        vertical? book_container_offHeight:
        book_container_offWidth
    );

    
    let page_top_par: HTMLParagraphElement | null;
    let skip_intersection: boolean = true;


    let pageScrollParam = $derived(
        vertical? (top:number) => { return {top: top} } :
        (left:number) => { return {left: left} }
    );


    let getInlineOffset = $derived(
        vertical? (el: HTMLElement) => { return el.offsetTop } :
        (el: HTMLElement) => { return el.offsetLeft }
    );

    let getBlockOffset = $derived(
        vertical? (el: HTMLElement) => { return el.offsetLeft } :
        (el: HTMLElement) => { return el.offsetTop }
    );


    function jumpTo(scroll_position: number) {
        book_container.scrollTo(
            pageScrollParam(Math.floor(scroll_position / book_container_offLenght) * book_container_offLenght)
        );
    }


    function nextPage(){
        skip_intersection = false;
        book_container.scrollBy(pageScrollParam(book_container_offLenght));
    }

    function prevPage(){
        skip_intersection = false;
        book_container.scrollBy(pageScrollParam(-book_container_offLenght));
    }


    let intersection_observer: IntersectionObserver;
    let resize_observer: ResizeObserver;

    function observeFirstColElements(){
        const elements = book_container.querySelectorAll("p[data-char-start]") as NodeListOf<HTMLParagraphElement>;
        let previous_offset: number = 0;
        let page: number = 0;

        elements.forEach(el => {
            const curr_offset = getInlineOffset(el);

            if (curr_offset >= previous_offset) {
                intersection_observer.observe(el);
                page++;
                previous_offset = page * book_container_offLenght;
            }
        });

        console.log(intersection_observer);
    }

    onMount(() => {
        page_top_par = null;

        intersection_observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !skip_intersection) {
                    page_top_par = entry.target as HTMLParagraphElement;

                    book_container_scrollPercent = vertical?
                        (book_container.scrollTop / book_container.scrollHeight) * 100:
                        (book_container.scrollLeft / book_container.scrollWidth) * 100;

                    console.log(page_top_par);
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
            }, 100);
        });

        resize_observer.observe(book_container);
        // intersection_observer.observe(page_top_par);
        observeFirstColElements();
    });


</script>

<svelte:head>
    {#each book.stylesheets as sheet_file}
        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/static/books/{book.id}/stylesheets/{sheet_file}" disabled>
    {/each}
</svelte:head>


<TopBar title={book.metadata.title}/>


{#if paginated}
    <!-- Left Arrow -->
    <button onclick={vertical? nextPage : prevPage} aria-label={vertical? "Next Page" : "Prev Page"} class="w-12 absolute left-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_right,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="m4 10l9 9l1.4-1.5L7 10l7.4-7.5L13 1z" />
        </svg>
    </button>
    <!-- Right Arrow -->
    <button onclick={vertical? prevPage : nextPage} aria-label={vertical? "Prev Page" : "Next Page"} class="w-12 absolute right-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_left,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="M7 1L5.6 2.5L13 10l-7.4 7.5L7 19l9-9z" />
        </svg>
    </button>
{/if}



<div bind:this={book_container} 
    bind:offsetHeight={book_container_offHeight}
    bind:offsetWidth={book_container_offWidth}
    class="jiku-book-container {vertical? "vert-rl" : "horz-tb!"} {paginated? "paginated overflow-hidden": "px-12 overflow-scroll!"} h-screen w-[calc(100vw-2*var(--book-x-margin))]! pt-14 pb-12 bg-neutral-800!" 
    style="{paginated? "--book-x-margin: 2rem;" : ""} line-height: 2.5rem; font-size: 20px"
>
    {@html content}
</div>



<div class="h-8 w-full fixed bottom-0 z-10">
    <div transition:scale class="h-2 bg-mist-700/95 absolute bottom-0 {vertical? "right-0 rounded-l-full": "left-0 rounded-r-full"} transition-[width] duration-200" style="width:{book_container_scrollPercent}%"></div>
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
        column-width: calc(100vw - var(--custom-gap));
        padding-inline: calc(var(--custom-gap) / 2);
    }

    .paginated {
        margin-left: var(--book-x-margin);
        margin-right: var(--book-x-margin);
    }


</style>
