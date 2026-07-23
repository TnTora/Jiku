<script lang="ts">
    import { clickOutside } from "$lib/utils/clickOutside";
    import { getConfirmationPopupContext } from "$lib/utils/context.svelte";
    import { getSelectCollectionPopupContext } from "./context";
    import { getJikuErrorsContext } from "$lib/utils/context.svelte";

    import { addBookToCollection, api_fetch, removeBookFromCollection } from "$lib/utils/requests";
	import CenteredPopup from "$lib/components/CenteredPopup.svelte";
	import SelectionPopup from "$lib/components/SelectionPopup.svelte";
	import { invalidateAll } from "$app/navigation";
	import { page } from "$app/state";
	import type { BookInfoResponse, BookProgressStatusUpdate } from "$lib/api_types/books";

    const confirmation_popup = getConfirmationPopupContext();
    const select_collection_popup = getSelectCollectionPopupContext();
    const errors = getJikuErrorsContext();

    let { item }: { item: BookInfoResponse} = $props();
    let show_item_options = $state(false);
    let show_stats = $state(false);
    let show_status_change = $state(false);

    let select_value: string | null = $state(null);

    interface Lemmas {
        total: number
        unique: number
        total_known: number
        unique_known: number
    }

    let lemmas_promise: Promise<Lemmas>;


    async function updateStatus() {
        if (!select_value) { return; }

        await api_fetch("books/set_progress_status", {
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: item.id,
                    new_status: select_value,
                } as BookProgressStatusUpdate)
            }, {
                err_msg: "Failed to updated progress status",
                err_context: errors,
        });

        invalidateAll();
        show_status_change = false;
        show_item_options = false;
        select_value = null;
    }

    async function loadKnownStats() {
        const res = await api_fetch(`books/known_stats/${item.id}`, {}, {
            err_msg: "Failed to load Known Stats",
            err_context: errors
        });
        const data = await res.json();
        return data;
    }

    async function deleteBook(book_id: number) {
        await api_fetch(
            `books/delete_book/${book_id}`, {
                method: "DELETE",
            }, {
                err_msg: `Failed to delete book ${book_id}`,
                err_context: errors,
            }
        );
        invalidateAll();
    }

</script>


<a href="{`/books/${item.id}`}" class="h-full w-full">
    <div
        class="book-item relative border border-neutral-600 active:border-neutral-400 active:border-2 bg-neutral-700 w-full h-full rounded-sm overflow-hidden cursor-pointer"
        style="{item.thumb? `background-image: url(${item.static_url}/${item.id}/images/${item.thumb});`: ""}"
    >
        <div class="relative h-full flex flex-col justify-between z-19 {item.thumb? "opacity-0 hover:opacity-100": ""} transition-opacity duration-100">
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

        <div class="absolute bottom-0 left-0 h-1 bg-sky-600" style="width:{item.progress_percent}%"></div>
        
    </div>
</a>

{#snippet option_button({text, onclick}: {text: string, onclick: () => void})}
    <button
        class="p-1 text-neutral-200 hover:text-sky-600 hover:bg-neutral-950 active:text-sky-400"
        onclick={(e) => {
            e.stopPropagation();
            onclick()
        }}
    >
    {text}
    </button>
{/snippet}

{#if show_item_options}
<div
    use:clickOutside
    onoutsideclick={() => { show_item_options = false; }}
    class="absolute w-full h-full flex flex-col justify-center gap-0 bg-neutral-900/99 z-30"
>

    {@render option_button({
        text: "Show Stats",
        onclick: () => { 
            lemmas_promise = loadKnownStats();
            show_stats = true;
        }
    })}

    {@render option_button({
        text: "Change Progress Status",
        onclick: () => { 
            show_status_change = true;
        }
    })}

    {#if page.url.searchParams.get("collection_id")}
        {@render option_button({
            text: "Remove from Collection",
            onclick: () => {
                const collection_id = Number(page.url.searchParams.get("collection_id"));
                confirmation_popup.onOk = async () => {
                    await removeBookFromCollection({
                        book_id: item.id,
                        collection_id: collection_id,
                        errors: errors,
                    });
                    invalidateAll()
                };
                confirmation_popup.text = `Remove '${item.title}' from current collection?`;
                confirmation_popup.show = true;
                show_item_options = false;
            }
        })}
    {:else}
        {@render option_button({
            text: "Add to Collection",
            onclick: () => {
                select_collection_popup.onOk = (collection_id:number) => {
                    addBookToCollection({
                        book_id: item.id,
                        collection_id: collection_id,
                        errors: errors,
                    });
                }
                select_collection_popup.show = true;
                show_item_options = false;
            }
        })}
    {/if}

    <button
        class="p-1 text-red-500 hover:text-red-500 hover:bg-neutral-950 active:text-red-400"
        onclick={() => {
            confirmation_popup.onOk = () => {
                deleteBook(item.id);
            };
            confirmation_popup.text = `Delete '${item.title}'?`;
            confirmation_popup.show = true;
            show_item_options = false;
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


{#if show_status_change}
    <SelectionPopup
        bind:select_value={select_value}
        text={"Select new status for " + item.title}
        options={[
            {value: "new", name: "new"},
            {value: "reading", name: "reading"},
            {value: "completed", name: "completed"},
        ]}
        onCancel={() => { show_status_change = false; }}
        onOk={updateStatus}
    />
{/if}


{#if show_stats}
    <CenteredPopup>
        <p>Known Lemmas for <span class="font-bold">{item.title}</span></p>
        {#await lemmas_promise}
            <svg class="w-10 h-10" fill="#6C89FF" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <g>
                    <circle cx="12" cy="2.5" r="1.5" opacity=".14"/>
                    <circle cx="16.75" cy="3.77" r="1.5" opacity=".29"/>
                    <circle cx="20.23" cy="7.25" r="1.5" opacity=".43"/>
                    <circle cx="21.50" cy="12.00" r="1.5" opacity=".57"/>
                    <circle cx="20.23" cy="16.75" r="1.5" opacity=".71"/>
                    <circle cx="16.75" cy="20.23" r="1.5" opacity=".86"/>
                    <circle cx="12" cy="21.5" r="1.5"/>
                    <animateTransform attributeName="transform" type="rotate" calcMode="discrete" dur="0.75s" values="0 12 12;30 12 12;60 12 12;90 12 12;120 12 12;150 12 12;180 12 12;210 12 12;240 12 12;270 12 12;300 12 12;330 12 12;360 12 12" repeatCount="indefinite"/>
                </g>
            </svg>
        {:then lemmas} 
            <p class="w-full text-left"><span class="font-bold">Total Known Lemmas:</span>  {lemmas.total_known} / {lemmas.total} ({(lemmas.total_known/lemmas.total*100).toFixed(2)}%)</p>
            <p class="w-full text-left"><span class="font-bold">Unique Known Lemmas:</span>  {lemmas.unique_known} / {lemmas.unique} ({(lemmas.unique_known/lemmas.unique*100).toFixed(2)}%)</p>
        {/await}
        
        <button
            class="mt-2 px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
            onclick={() => { show_stats = false; }}
        >
            Close
        </button>
    </CenteredPopup>
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