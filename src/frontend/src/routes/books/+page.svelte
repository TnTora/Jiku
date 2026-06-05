<script lang="ts">
    import { fly } from "svelte/transition";
    import { SvelteSet } from "svelte/reactivity";
    import { page } from "$app/state";
    import BookGridDisplay from "./BookGridDisplay.svelte";
    import TopBar from "./TopBar.svelte";
    import SidePanel from "./SidePanel.svelte";
    import SelectCollection from "./SelectCollection.svelte";
    import { getJikuErrorsContext } from "$lib/utils/context";
    import { getConfirmationPopupContext } from "$lib/utils/context";
    import { setSelectColelctionPopupContext } from "./context.js";
	import { goto, invalidateAll } from "$app/navigation";
	import { onMount } from "svelte";

    import { addBookToCollection } from "./requests.js";

    import type { SelectCollectionPopupContext } from "./context.js";


    const errors = getJikuErrorsContext();
    const confirmation_popup = getConfirmationPopupContext();

    let { data } = $props();

    // svelte-ignore state_referenced_locally
    let { collections } = $state(data);

    let ascending_order: boolean = $state(Boolean(page.url.searchParams.get("asc")));
    let item_size_rem: number = $state(12.5);
    let show_side_panel: boolean = $state(false);
    let selecting: boolean = $state(false);
    let selected = $state(new SvelteSet());
    let title_search: string = $state("");


    let select_collection_popup: SelectCollectionPopupContext = $state({
        show: false,
        selected_id: null,
        onOk: (collection_id: number) => {},
    })

    setSelectColelctionPopupContext(select_collection_popup)

    $effect(() => {
        // console.log(selecting);
        // console.log(selected);
        // console.log(select_add_collection_id);
        if (!selecting) {
            selected.clear();
        }
    });

    async function deleteSelectedBooks() {
        for (const book of selected) {

            try {
                const res = await fetch(`http://127.0.0.1:8000/books/delete_book/${book.id}`, {
                    method: "DELETE",
                });
            } catch (error) {
                console.error(`Failed deleting book ${book.title}`, error);
                errors.push({
                    short: "Failed deleting collection",
                    details: error,
                });
                throw error;
            }

        }

        invalidateAll();
    }


    function modifiedSearchParams( key: string, value: string) {
        const search_params = new URLSearchParams(page.url.searchParams);
        if (value) {
            search_params.set(key, value);
        } else {
            search_params.delete(key);
        }
        
        return `?${search_params.toString()}`;
    }

    function searchTitle() { 
        goto(modifiedSearchParams("title", title_search));
    }

    onMount(() => {
        title_search = page.url.searchParams.get("title")?? "";
    });

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
            <SidePanel collections={collections} creators={data.creators}/>
        </div>
    {/if}


    <div style="grid-area: options;">
        <div class="w-full px-4 py-2 flex justify-between items-center gap-x-3 ">
            <!-- Search Bar -->

            <select
                id="status"
                class="px-2 py-1 text-md text-center shrink-2 min-w-13 bg-neutral-900 border-neutral-900 hover:bg-neutral-950 border rounded-lg"
                onchange={function(this: HTMLSelectElement) {goto(modifiedSearchParams("progress", this.value))}}
            >
                <option value="">All</option>
                <option value="reading">Reading</option>
                <option value="completed">Completed</option>
                <option value="new">New</option>
            </select>

            <input
                bind:value={title_search}
                type="text"
                placeholder="Enter Book Title"
                class="px-3 py-1 text-sm grow shrink w-0 bg-neutral-600 border-neutral-700 hover:border-neutral-500 focus:border-neutral-500 border rounded-md"
                onkeydown={(event) => {
                    if (event.code === "Enter") { 
                        searchTitle();
                    }
                }}
            >

            <button
                title="Search"
                class="px-2 py-1 text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
                onclick={searchTitle}
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
                    onchange={function(this: HTMLSelectElement) {
                        const search_params = new URLSearchParams(page.url.searchParams);
                        if (Number(this.value) > 0) {
                            search_params.set("asc", "no");
                            ascending_order = false;
                        }
                        search_params.set("ordr", this.value);
                        goto(`?${search_params.toString()}`);
                    }}
                >
                    <option value="0">Title</option>
                    <option value="1">Last Added</option>
                    <option value="2">Last Opened</option>
                </select>

                <button
                    title="Order Toggle"
                    class="px-2 py-1 text-sm bg-neutral-900 border-neutral-900 hover:bg-neutral-950 active:bg-[#353535] border rounded-lg"
                    onclick={() => {
                        if (ascending_order) {
                            goto(modifiedSearchParams("asc", "no"))
                        } else {
                            goto(modifiedSearchParams("asc", ""))
                        }
                        ascending_order = !ascending_order
                    }}
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
        <BookGridDisplay bind:selected={selected} bind:selecting={selecting} items={data.books} item_min_w={`${item_size_rem}rem`}/>
    </div>

    <div class="h-8 px-3 py-2 flex items-center justify-between" style="grid-area: footer">
        <div class="flex items-center justify-start gap-3">
        {#if selecting}
            <button
                title="Delete"
                class="text-sm text-red-500 hover:text-red-700 active:text-red-400 hover:cursor-pointer"
                onclick={() => {
                    if (selected.size == 0) { return; }

                    confirmation_popup.onOk = async () => {
                        try {
                            await deleteSelectedBooks();
                            selecting = false;
                        } catch (error) {
                            console.error(error.message);
                        }
                    }
                    confirmation_popup.text = `Delete ${selected.size} books?`
                    confirmation_popup.show = true;
                    
                }}
            >
                Delete
            </button>
            <button
                title="Add to Collection"
                class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => {
                    if (selected.size == 0) { return; }

                    select_collection_popup.onOk = (collection_id:number) => {
                        let task: Array<Promise<void>> = []
                        console.log("adding")
                        for (const book of selected) {
                            console.log(book);
                            task.push(addBookToCollection(book.id, errors)(collection_id));
                        }
                        Promise.allSettled(task)
                        .then(() => selecting = false)
                    }
                    select_collection_popup.show = true;
                    
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

{#if select_collection_popup.show}
    <SelectCollection 
        bind:select_value={select_collection_popup.selected_id}
        text="Select Collection"
        {collections}
        onCancel={() => {
            select_collection_popup.show = false;
            select_collection_popup.selected_id = null;
        }}
        onOk={() => {
            console.log("select_collection_popup.selected_id", select_collection_popup.selected_id);
            if (select_collection_popup.selected_id) {
                select_collection_popup.onOk(select_collection_popup.selected_id);
            }
            select_collection_popup.show = false;
            select_collection_popup.selected_id = null;
        }}
    />
{/if}

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