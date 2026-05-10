<script lang="ts">
    import GridDisplay from "$lib/components/GridDisplay.svelte";
    import TopBar from "./TopBar.svelte";
    let { data } = $props();
    let  ascending_order: boolean = $state(false);
    let item_size_rem: number = $state(12.5);
</script>

<div class="flex flex-col h-screen">
    <div class="shrink-0 h-11 w-full bg-neutral-900">
        <TopBar/>
    </div>

    <div class="w-full px-4 py-2 flex justify-between items-center gap-x-3 ">
        <!-- Search Bar -->

        <select
            id="status"
            class="px-2 py-1 text-md text-center shrink-2 min-w-13 bg-neutral-900 border-neutral-900 hover:bg-neutral-950 border rounded-lg"
        >
            <option>All</option>
            <option>Reading</option>
            <option>Completed</option>
            <option>New</option>
        </select>

        <input
            type="text"
            placeholder="Enter Book Title"
            class="px-3 py-1 text-sm grow shrink min-w-15 bg-neutral-600 border-neutral-700 hover:border-neutral-500 focus:border-neutral-500 border rounded-md"
        >

        <button
            title="Search"
            class="px-2 py-1 text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
        >
            Search
        </button>
    </div>

    <div class="w-full px-4 py-2 flex justify-between items-center gap-x-3 ">

        <div class="ml-1 flex gap-2 justify-between items-center">
            <!-- Order By -->

            <select
                id="order-by"
                class="px-2 py-1 text-sm field-sizing-content text-center bg-neutral-900 border-neutral-900 hover:bg-neutral-950 border rounded-lg"
            >
                <option>Title</option>
                <option>Length</option>
                <option>Known Unique Words %</option>
                <option>Known Total Words %</option>
            </select>

            <button
                title="Order Toggle"
                class="px-2 py-1 text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
                onclick={() => {ascending_order = !ascending_order}}
            >
                {#if ascending_order}
                    <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
                        <path fill="currentColor" d="M4.5 14c-.28 0-.5-.22-.5-.5v-9c0-.28.22-.5.5-.5s.5.22.5.5v9c0 .28-.22.5-.5.5" />
                        <path fill="currentColor" d="M8 7.5a.47.47 0 0 1-.35-.15L4.5 4.2L1.35 7.35c-.2.2-.51.2-.71 0s-.2-.51 0-.71l3.5-3.5c.2-.2.51-.2.71 0l3.5 3.5c.2.2.2.51 0 .71c-.1.1-.23.15-.35.15" />
                    </svg>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
                        <path fill="currentColor" d="M4.5 13c-.28 0-.5-.22-.5-.5v-9c0-.28.22-.5.5-.5s.5.22.5.5v9c0 .28-.22.5-.5.5" />
                        <path fill="currentColor" d="M4.5 14a.47.47 0 0 1-.35-.15l-3.5-3.5c-.2-.2-.2-.51 0-.71s.51-.2.71 0l3.15 3.15l3.15-3.15c.2-.2.51-.2.71 0s.2.51 0 .71l-3.5 3.5c-.1.1-.23.15-.35.15Z" />
                    </svg>
                {/if}
            </button>
        </div>

        <div class="mr-1 flex gap-1 justify-between items-center">
            <!-- Item Size -->
            <span
                class="mr-2"
            >
                Size:
            </span>
            <button
                title="Reduce Size"
                class="w-6 aspect-square text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
                onclick={() => {
                    if (item_size_rem <= 6.5) { return; }
                    item_size_rem--;
                }}
            >
                -
            </button>
            <button
                title="Increase Size"
                class="w-6 aspect-square text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
                onclick={() => {item_size_rem++;}}
            >
                +
            </button>

        </div>
    </div>

    <GridDisplay items={data.books} item_min_w={`${item_size_rem}rem`}/>
</div>

<style>

input:focus {
  outline: none;
}

</style>