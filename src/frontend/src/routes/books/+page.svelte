<script lang="ts">
    import { fly } from "svelte/transition";
    import { SvelteSet } from "svelte/reactivity";
    import GridDisplay from "$lib/components/GridDisplay.svelte";
    import TopBar from "./TopBar.svelte";
    import SidePanel from "./SidePanel.svelte";
    let { data } = $props();
    let  ascending_order: boolean = $state(false);
    let item_size_rem: number = $state(12.5);
    let show_side_panel: boolean = $state(false);
    let selecting: boolean = $state(false);
    let selected = new SvelteSet();
    $effect(() => {
        // console.log(selecting);
        // console.log(selected);
        if (!selecting) {
            selected.clear();
        }
    });

    function onItemClickCapture(item) {
        return (e) => {
            if (!selecting) { return; }

            console.log("selected", selected);

            e.stopPropagation();
            e.preventDefault();

            if (selected.has(item)){
                selected.delete(item);
            } else {
                selected.add(item);
            }
        }
    };
</script>

<div class="main-container h-screen overflow-hidden">
    <div class="h-11 w-full bg-neutral-900" style="grid-area: header;">
        <TopBar bind:show_side_panel={show_side_panel} toggleSidePanel={() => { show_side_panel = !show_side_panel }}/>
    </div>

    {#if show_side_panel}
        <div
            transition:fly={{x:-320, duration:200, opacity:0.5}}
            class="h-full" style="grid-area: sidepanel;"
        >
            <SidePanel onoutsideclick={() => { show_side_panel = false; }}/>
        </div>
    {/if}


    <div style="grid-area: options;">
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
                class="px-3 py-1 text-sm grow shrink w-0 bg-neutral-600 border-neutral-700 hover:border-neutral-500 focus:border-neutral-500 border rounded-md"
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
                        if (item_size_rem <= 8.5) { return; }
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
    </div>

    <div class="overflow-y-scroll" style="grid-area: main;">
        <GridDisplay {onItemClickCapture} {selected} items={data.books} item_min_w={`${item_size_rem}rem`}/>
    </div>

    <div class="h-8 px-2 py-2 flex items-center justify-between" style="grid-area: footer">
        <div class="flex items-center justify-start gap-3">
        {#if selecting}
            <button
                title="Delete"
                class="text-sm text-red-500 hover:text-red-700 active:text-red-400 hover:cursor-pointer"
                onclick={() => {
                    selecting = false;
                }}
            >
                Delete
            </button>
            <button
                title="Add to Collection"
                class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => {
                    selecting = false;
                }}
            >
                Add to Collection
            </button>
        {/if}
        </div>
        <div class="flex items-center justify-end gap-3">
        {#if selecting}
            <button
                title="Cancel"
                class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => {
                    selecting = false;
                }}
            >
                Cancel
            </button>
            <button
                title="Select All"
                class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => {
                    data.books.forEach((item) => { selected.add(item); });
                }}
            >
                Select All
            </button>
        {:else}
            <button
                title="Select"
                class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => {
                    selecting = true;
                }}
            >
                Select
            </button>
        {/if}
        </div>
    </div>
    
</div>

<style>

input:focus {
  outline: none;
}

.main-container {
    display: grid;
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto 1fr auto;
    grid-template-areas: 
    "header header"
    "sidepanel options"
    "sidepanel main"
    "sidefooter footer";
    transition: all 500ms;
}

</style>