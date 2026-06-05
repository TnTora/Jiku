<script lang="ts">
    import { clickOutside } from "$lib/utils/clickOutside";
    import { fly } from "svelte/transition";
    import { getTextInputPopupContext, getConfirmationPopupContext } from "$lib/utils/context";

    let { book, onoutsideclick, updatePosition } = $props();

    let confirmation_popup = getConfirmationPopupContext();
    let text_input_popup = getTextInputPopupContext();

    let tab: "toc" | "spine" | "bookmarks" = $state("toc");
    let editing: boolean = $state(false);


    async function renameBookmark(bookmark_id:number) {
        let name = text_input_popup.text_input_value;

        try {
            let res = await fetch("http://127.0.0.1:8000/books/rename_bookmark/", {
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: bookmark_id,
                    name: name
                })
            });
        } catch (error) {
            console.error("Failed to rename bookmark", error);
            errors.push({
                short: "Failed to rename bookmark",
                details: error,
            });
            throw error;
        }
    }


    async function deleteBookmark(bookmark_id: number) {
        try {
            const res = await fetch(`http://127.0.0.1:8000/books/delete_bookmark/${bookmark_id}`, {
                method: "DELETE",
            });
        } catch (error) {
            console.error("Failed deleting bookmark", error);
            errors.push({
                short: "Failed deleting bookmark",
                details: error,
            });
            throw error;
        }
    }

</script>

<div
    transition:fly={{x:-320, duration:200, opacity:0.5}}
    use:clickOutside={"button[title=TOC]"}
    {onoutsideclick}
    class="absolute top-0 w-80 bg-neutral-800 border-neutral-600 h-full overflow-scroll z-20"
>
    
    <div id="tabs" class="mt-4 mb-4 mx-4 py-3 bg-[#1B1B1B] rounded-full border border-neutral-900 sticky top-0 flex items-center justify-evenly gap-5 font-semibold text-sm">
        <button title="TOC" onclick={() => { tab = "toc" }} class="{(tab == "toc")?"underline underline-offset-4":""}">
            TOC
        </button>

        <button title="Spine" onclick={() => { tab = "spine" }} class="{(tab == "spine")?"underline underline-offset-4":""}">
            Spine
        </button>

        <button title="Bookmarks" onclick={() => { tab = "bookmarks" }} class="{(tab == "bookmarks")?"underline underline-offset-4":""}">
            Bookmarks
        </button>
    </div>

    {#if tab == "toc"}
        <ul>
        {#each book.toc as entry}
            <li>
                <button onclick={() => { updatePosition(entry.section, null, entry.anchor_id) }}>
                    {entry.title}
                </button>
            </li>
        {/each}
        </ul>
    {:else if tab == "spine"}
        <ul>
        {#each book.spine as entry}
            <li>
                <button onclick={() => { updatePosition(entry) }}>
                    {entry}
                </button>
            </li>
        {/each}
        </ul>
    {:else}
        <ul class="h-full">
        {#each book.bookmarks as entry}
            <li class="flex items-center justify-between {editing? "editing": ""}">
                <button
                    class="mr-3 grid grid-cols-[1fr_auto] grid-rows-[auto_auto] gap-x-3 justify-between items-center"
                    onclick={() => { updatePosition(entry.section, entry.tok_pos) }}
                >
                    <span class="col-start-1 col-end-2 row-start-1 row-end-2">{entry.name}</span>
                    <span class="col-start-1 col-end-2 row-start-2 row-end-3 text-sm max-h-10 overflow-y-scroll text-neutral-400">{entry.preview}</span>
                    <span class="col-start-2 col-end-3 row-start-1 row-end-3">{entry.tok_pos}</span>
                    
                </button>
                {#if editing}
                    <div class="flex gap-1">
                        <button title="Rename"
                            class="hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                            onclick={(e) => {
                                e.stopPropagation();

                                text_input_popup.onOk = async () => {
                                    if (!text_input_popup.text_input_value) { return; }

                                    try {
                                        await renameBookmark(entry.id)
                                        entry.name = text_input_popup.text_input_value;
                                    } catch (error) {
                                        console.error(error.message);
                                    }

                                }
                                text_input_popup.text = `Rename bookmark '${entry.name}' to:`;
                                text_input_popup.text_input_default = entry.name;
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
                                        await deleteBookmark(entry.id);
                                        book.bookmarks = book.bookmarks.filter( e => e.id != entry.id);
                                    } catch (error) {
                                        console.error(error);
                                    }
                                }
                                confirmation_popup.text = `Delete bookmark '${entry.name}'?`
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
        {#if editing}
            <button
                title="Edit Done"
                class="sticky bottom-0 text-sm w-full px-4 pt-1 pb-2 text-left bg-neutral-800 text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => { editing = false; }}
            >
                Done
            </button>
        {:else}
            <button
                title="Edit"
                class="sticky bottom-0 text-sm w-full px-4 pt-1 pb-2 text-left bg-neutral-800 text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                onclick={() => { editing = true; }}
            >
                Edit
            </button>
        {/if}
    {/if}
</div>


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

li:active {
    background-color: #1A1A1A;
}

</style>