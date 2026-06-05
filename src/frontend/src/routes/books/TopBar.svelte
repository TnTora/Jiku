<script lang="ts">
    import { getTasksContext } from "$lib/utils/taskEventSource.svelte";

    let task_context = getTasksContext();

    console.log(task_context);

    let { toggleSidePanel, show_side_panel=$bindable() } = $props();
    let btn_shared_classes = "hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";

    async function handleFilesInput (this: HTMLInputElement) {
        if (!this.files) { return; }
        console.log("files input");

        task_context.connect();

        for (const file of this.files) {
            console.log(file.name);
            const formData = new FormData();
            formData.append("file", file, file.name);
            await fetch(`http://127.0.0.1:8000/books/add_book`, {
                method: "POST",
                body: formData,
            })
        }
    }

</script>

<div class="bg-neutral-800 h-11 w-full flex justify-between items-center gap-x-1.5 z-20">
    <div class="h-full flex justify-start gap-4 ml-4 items-center">
        {#if !show_side_panel}
            <button class="{btn_shared_classes}" title="Open Sidepanel" onclick={toggleSidePanel}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M4 17q-.425 0-.712-.288T3 16t.288-.712T4 15h12q.425 0 .713.288T17 16t-.288.713T16 17zm0-4q-.425 0-.712-.288T3 12t.288-.712T4 11h12q.425 0 .713.288T17 12t-.288.713T16 13zm0-4q-.425 0-.712-.288T3 8t.288-.712T4 7h12q.425 0 .713.288T17 8t-.288.713T16 9zm16 8q-.425 0-.712-.288T19 16t.288-.712T20 15t.713.288T21 16t-.288.713T20 17m0-4q-.425 0-.712-.288T19 12t.288-.712T20 11t.713.288T21 12t-.288.713T20 13m0-4q-.425 0-.712-.288T19 8t.288-.712T20 7t.713.288T21 8t-.288.713T20 9" />
                </svg>
            </button>
        {:else}
            <button class="{btn_shared_classes}" title="Close Sidepanel" onclick={toggleSidePanel}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 15 15">
                    <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
                </svg>
            </button>
    {/if}
    </div>

    <div class="h-full flex justify-end gap-4 mr-4 items-center">
        <label>
            <svg class="h-8 {btn_shared_classes}" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5">
                    <path d="M20 22H6a2 2 0 0 1-2-2m0 0a2 2 0 0 1 2-2h14V6c0-1.886 0-2.828-.586-3.414S17.886 2 16 2h-6c-2.828 0-4.243 0-5.121.879C4 3.757 4 5.172 4 8z" />
                    <path d="M19.5 18s-1 .763-1 2s1 2 1 2M9 10s2.21-3 3-3s3 3 3 3m-3-2.5V13" />
                </g>
            </svg>
            <input type="file" multiple accept=".epub" title="Upload" style="display: none;"
                oninput={handleFilesInput}
            >
        </label>
    </div>
</div>


<style>
    svg {
        margin: auto;
    }
</style>