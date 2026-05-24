<script lang="ts">
    import { clickOutside } from "$lib/utils/clickOutside";
    import { getConfirmationPopupContext } from "$lib/utils/context";

    const confirmation_popup = getConfirmationPopupContext();

    let { item, deleteBook } = $props();
    let show_item_options = $state(false);

</script>


<a href="{`/books/${item.id}`}" class="h-full w-full">
    <div
        class="book-item border border-neutral-600 active:border-neutral-400 active:border-2 bg-neutral-700 w-full h-full rounded-lg overflow-hidden cursor-pointer"
        style="background-image: url({item.static_url}/{item.id}/images/{item.thumb});"
    >
        <div class="relative h-full flex flex-col justify-between {item.thumb? "opacity-0 hover:opacity-100": ""} transition-opacity duration-100">
            <div class="bg-neutral-700/80 text-neutral-300 text-sm h-fit p-1">
                {item.title}
            </div>
        
            <div class="bg-neutral-700/80 text-neutral-300 text-xs h-fit p-1">
                {#each item.creators as creator}
                    {creator};
                {/each}
            </div>

            <button
                title="Item Options"
                class="absolute options bottom-0.5 right-1 aspect-square h-5 w-5 hover:text-sky-300 active:text-sky-500 cursor-pointer z-20"
                onclick={(e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    show_item_options = true;
                }}
            >
                <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
                    <g fill="currentColor">
                        <path d="M176 32v192a16 16 0 0 1-16 16H96a16 16 0 0 1-16-16V32a16 16 0 0 1 16-16h64a16 16 0 0 1 16 16" opacity="0.2" />
                        <path d="M140 128a12 12 0 1 1-12-12a12 12 0 0 1 12 12m-12-56a12 12 0 1 0-12-12a12 12 0 0 0 12 12m0 112a12 12 0 1 0 12 12a12 12 0 0 0-12-12" />
                    </g>
                </svg>
            </button>
        </div>
        
    </div>
</a>

{#if show_item_options}
<div
    use:clickOutside
    onoutsideclick={() => { show_item_options = false; }}
    class="absolute w-full h-full flex flex-col justify-center gap-0 bg-neutral-900/99"
>
    <button class="p-1 text-neutral-200 hover:text-sky-600 hover:bg-neutral-950 active:text-sky-400">
        Metadata
    </button>
    <button class="p-1 text-neutral-200 hover:text-sky-600 hover:bg-neutral-950 active:text-sky-400">
        Add to Collection
    </button>
    <button
        class="p-1 text-red-500 hover:text-red-500 hover:bg-neutral-950 active:text-red-400"
        onclick={(e) => {
            e.stopPropagation();
            confirmation_popup.modalOk = async () => {
                try {
                    await deleteBook(item.id);
                } catch (error) {
                    console.error(error);
                }
            }
            confirmation_popup.use_modal_input = false;
            confirmation_popup.input_description = `Delete '${item.title}'?`
            confirmation_popup.show_input_modal = true;
        }}
    >
        Delete
    </button>
    <button
        title="Close"
        class="absolute bottom-2 right-2 text-neutral-200 hover:text-sky-600 active:text-sky-400 cursor-pointer"
        onclick={() => { show_item_options = false; }}
    >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4" viewBox="0 0 15 15">
            <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
        </svg>
    </button>
</div>
{/if}


<style>

.book-item {
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

.book-item:has( button.options:active) {
    border: 0rem;
}

</style>