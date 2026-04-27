<script lang="ts">
	import TopBar from "./TopBar.svelte";
    let { data } = $props();
    let { book, content } = data;
    let vertical = $state(true);
    let paginated = $state(true);
    console.log(book);

    let book_container: HTMLDivElement;
    let book_container_boxsize;


    function changePageHorizontal(reverse: boolean = false){
        let width = book_container.getBoundingClientRect().width;
        if (reverse) {
            return () => { book_container.scrollBy(-width, 0); };
        } else {
            return () => { book_container.scrollBy(width, 0); };
        }
    }

    function changePageVertical(reverse: boolean = false){
        let height = book_container.getBoundingClientRect().height;
        console.log(height);
        if (reverse) {
            return () => { book_container.scrollBy(0, -height); };
        } else {
            return () => { book_container.scrollBy(0, height); };
        }
    }

</script>

<svelte:head>
    {#each book.stylesheets as sheet_file}
        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/static/books/{book.id}/stylesheets/{sheet_file}" disabled>
    {/each}
</svelte:head>


<TopBar title={book.metadata.title}/>


{#if paginated}
    <!-- Left Arrow -->
    <button onclick={vertical? changePageVertical() : changePageHorizontal(true)} aria-label={vertical? "Next Page" : "Prev Page"} class="w-12 absolute left-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_right,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="m4 10l9 9l1.4-1.5L7 10l7.4-7.5L13 1z" />
        </svg>
    </button>
    <!-- Right Arrow -->
    <button onclick={vertical? changePageVertical(true) : changePageHorizontal()} aria-label={vertical? "Prev Page" : "Next Page"} class="w-12 absolute right-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_left,#333,transparent] h-screen z-10">
        <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path fill="currentColor" d="M7 1L5.6 2.5L13 10l-7.4 7.5L7 19l9-9z" />
        </svg>
    </button>
{/if}



<div bind:this={book_container} 
    bind:contentBoxSize={book_container_boxsize}
    class="jiku-book-container {vertical? "vert-rl" : "horz-tb!"} {paginated? "paginated overflow-hidden": "px-12 overflow-scroll!"} h-screen w-[calc(100vw-2*var(--book-x-margin))]! pt-14 pb-12 bg-neutral-800!" 
    style="{paginated? "--book-x-margin: 2rem;" : ""} line-height: 2.5rem; font-size: 20px"
>
    {@html content}
</div>



<div class="h-8 w-full fixed bottom-0 z-10">
    <div class="h-2 bg-mist-700/95 absolute bottom-0 {vertical? "right-0 rounded-l-full": "left-0 rounded-r-full"}" style="width:{50}%"></div>
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
