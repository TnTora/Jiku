<script lang="ts">
    import { getJikuErrorsContext, getTextInputPopupContext, getConfirmationPopupContext } from "$lib/utils/context.svelte";
    import { page } from "$app/state";
	import { goto } from "$app/navigation";
	import { api_fetch } from "$lib/utils/requests";
	import type { CollectionCreate, CollectionInfoResponse, CollectionRename, CreatorInfoRespone } from "$lib/api_types/books";

    const errors = getJikuErrorsContext();
    const confirmation_popup = getConfirmationPopupContext();
    const text_input_popup = getTextInputPopupContext();


    // let collections_test = [];

    // for (let i=0; i < 20; i++) {
    //     collections_test.push({
    //         id: i,
    //         name: `Collection ${i+1}`
    //     });
    // }

    interface Props {
        collections: CollectionInfoResponse[],
        creators: CreatorInfoRespone[]
    }

    let { collections, creators }: Props = $props();

    let tab: "collections" | "authors" = $state("collections");

    let editing: boolean = $state(false);


    async function addCollection() {
        let new_collection: CollectionInfoResponse;
        let name = text_input_popup.text_input_value;

        try {
            let res = await api_fetch("books/add_collection/", {
                method: "POST",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: name
                } as CollectionCreate)
            }, {
                err_msg: "Failed to add new collection",
                err_context: errors,
            });
            new_collection = await res.json();
        } catch (error) {
            throw error;
        }

        if (new_collection) {
            collections.push(new_collection);
        }
        
    }


    async function renameCollection(collection_id:number) {
        let name = text_input_popup.text_input_value;

        await api_fetch("books/rename_collection", {
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: collection_id,
                    name: name
                } as CollectionRename)
            }, {
                err_msg: "Failed to rename collection",
                err_context: errors
        });
    }


    async function deleteCollection(collection_id: number) {
        await api_fetch(`books/delete_collection/${collection_id}`, {
                method: "DELETE",
            }, {
                err_msg: "Failed deleting collection",
                err_context: errors,
            })
    }

</script>

<div
    class="relative w-80 border-neutral-600 border-r h-full overflow-scroll z-20"
>
    
    <div id="tabs" class="mb-4 mx-2 py-3 bg-[#1B1B1B] rounded-md border border-neutral-900 sticky top-0 flex items-center justify-evenly gap-5 font-semibold text-sm">
        <button title="Collections" onclick={() => { tab = "collections" }} class="{(tab == "collections")?"underline underline-offset-4":""}">
            Collections
        </button>

        <button title="Authors" onclick={() => { tab = "authors" }} class="{(tab == "authors")?"underline underline-offset-4":""}">
            Authors
        </button>
    </div>

    {#if tab == "collections"}
        <ul>
            <li>
                <a href={page.url.pathname} class="w-auto block">
                    Library
                </a>
            </li>
        {#each collections as collection}
            <li class="flex items-center justify-between {editing? "editing": ""}">
                <a href="?collection_id={collection.id}" class="grow">
                    {collection.name}
                </a>
            {#if editing}
                <div class="flex gap-1">
                    <button title="Rename"
                        class="hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                        onclick={(e) => {
                            e.stopPropagation();

                            text_input_popup.onOk = async () => {
                                if (!text_input_popup.text_input_value) { return; }

                                try {
                                    await renameCollection(collection.id)
                                    collection.name = text_input_popup.text_input_value;
                                } catch (error: any) {
                                    console.error(error.message);
                                }

                            }
                            text_input_popup.text = `Rename Collection '${collection.name}' to:`;
                            text_input_popup.text_input_default = collection.name;
                            text_input_popup.show = true;
                        }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                            <path fill="currentColor" d="M14.5 2a.48.48 0 0 1 .352.148A.48.48 0 0 1 15 2.5a.48.48 0 0 1-.148.352A.48.48 0 0 1 14.5 3H13v14h1.5a.48.48 0 0 1 .352.148a.48.48 0 0 1 .148.352a.48.48 0 0 1-.148.352a.48.48 0 0 1-.352.148h-4a.48.48 0 0 1-.352-.148A.48.48 0 0 1 10 17.5a.48.48 0 0 1 .148-.352A.48.48 0 0 1 10.5 17H12V3h-1.5a.48.48 0 0 1-.352-.148A.48.48 0 0 1 10 2.5a.48.48 0 0 1 .148-.352A.48.48 0 0 1 10.5 2zM11 5H5q-.414 0-.773.156a2.1 2.1 0 0 0-.641.43a1.9 1.9 0 0 0-.43.633Q3.008 6.579 3 7v6q0 .414.156.773q.157.36.43.641t.633.43T5 15h6v1H5q-.625 0-1.164-.234a3.1 3.1 0 0 1-.953-.641A2.95 2.95 0 0 1 2 13V7q0-.617.234-1.164a3 3 0 0 1 .641-.953q.406-.406.953-.649Q4.375 3.992 5 4h6zm4-1q.618 0 1.164.234a3 3 0 0 1 1.602 1.602Q18.008 6.39 18 7v6q0 .625-.234 1.164q-.235.54-.641.953q-.406.414-.96.649A3 3 0 0 1 15 16h-1v-1h1q.414 0 .773-.156a2.1 2.1 0 0 0 .641-.43a1.9 1.9 0 0 0 .43-.633q.148-.36.156-.781V7a1.9 1.9 0 0 0-.156-.773a2.1 2.1 0 0 0-.43-.641a1.9 1.9 0 0 0-.633-.43Q15.421 5.008 15 5h-1V4zM7.5 6a.5.5 0 0 1 .454.292l2.75 6a.5.5 0 1 1-.908.416l-.784-1.71L9 11H6l-.013-.002l-.783 1.71a.5.5 0 1 1-.908-.416l2.75-6l.034-.063A.5.5 0 0 1 7.5 6m-1.055 4h2.11L7.5 7.698z" />
                        </svg>
                    </button>
                    <button title="Delete"
                        class="text-red-500 hover:text-red-800 active:text-red-400 hover:cursor-pointer"
                        onclick={(e) => {
                            e.stopPropagation();
                            confirmation_popup.onOk = async () => {
                                try {
                                    await deleteCollection(collection.id);
                                    collections = collections.filter( e => e.id != collection.id);
                                    if (page.url.searchParams.get("collection_id") == collection.id.toString()) {
                                        goto(page.url.pathname);
                                    }
                                } catch (error) {
                                    console.error(error);
                                }
                            }
                            confirmation_popup.text = `Delete Collection '${collection.name}'?`
                            confirmation_popup.show = true;
                        }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12l1.41 1.41L13.41 14l2.12 2.12l-1.41 1.41L12 15.41l-2.12 2.12l-1.41-1.41L10.59 14zM15.5 4l-1-1h-5l-1 1H5v2h14V4z" />
                        </svg>
                    </button>
                </div>
            {/if}
            </li>
        {/each}
        </ul>

    {:else if tab == "authors"}
        <ul>
        {#each creators as creator}
            <li>
                <a href={`?creator_id=${creator.id}`} class="w-auto block">
                    {creator.name}
                </a>
            </li>
        {/each}
        </ul>
    {/if}
</div>


{#if tab == "collections"}
<div class="bg-neutral-800 border-neutral-700 border-t border-r border-r-neutral-600 flex items-center justify-between text-xs text-neutral-300" style="grid-area: sidefooter;">
    <div class="px-5 pt-0.5 pb-1 flex items-center gap-4">
    {#if editing}
        <button
            title="Edit Done"
            class="hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
            onclick={() => { editing = false; }}
        >
            Done
        </button>
    {:else}
        <button
            title="Edit Collection"
            class="hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
            onclick={() => { editing = true; }}
        >
            Edit Collections
        </button>
    {/if}
    </div>
    <button
        title="New Collection"
        class="h-full text-xs bg-neutral-900 border-neutral-700 hover:bg-neutral-950 active:bg-[#353535]"
        onclick={() => {
            console.log("input modal");
            text_input_popup.show = true;
            text_input_popup.text = "Choose a name for the new collection";
            text_input_popup.onOk = addCollection;
        }}
    >
        <svg xmlns="http://www.w3.org/2000/svg" width="1.25rem" height="1.25rem" viewBox="0 0 24 24">
            <path fill="currentColor" d="M18 12.998h-5v5a1 1 0 0 1-2 0v-5H6a1 1 0 0 1 0-2h5v-5a1 1 0 0 1 2 0v5h5a1 1 0 0 1 0 2" />
        </svg>        
    </button>
    <!-- <div class="flex items-center">
        <button
            title="New Collection"
            class="aspect-square h-full text-xs bg-neutral-900 border-neutral-700 hover:bg-neutral-950 active:bg-[#353535]"
            onclick={() => {
                console.log("input modal");
                text_input_popup.show = true;
                text_input_popup.text = "Choose a name for the new collection";
                text_input_popup.onOk = addCollection;
            }}
        >
            +
        </button>
    </div> -->
</div>
{/if}

<style>

button {
    cursor: pointer;
}

li > button {
    width: 100%;
    text-align: left;
}

ul {
    padding-bottom: 1.5rem;
}

li {
    padding-inline: 1.5rem;
    padding-block: 0.25rem;
    cursor: pointer;
}

li:hover {
    background-color: #333;
}

li:not(.editing):active {
    background-color: #1A1A1A;
}

</style>