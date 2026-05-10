<script>
    // let { title, toggleOptions, toggleSidePanel,} = $props();
    let btn_shared_classes = "hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";
</script>

<div class="bg-neutral-800 h-11 w-full flex justify-between items-center gap-x-1.5 z-20">
    <div class="h-full flex justify-start gap-4 ml-4 items-center">
        <button class="{btn_shared_classes}" title="TOC" onclick={() => {}}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8" viewBox="0 0 24 24">
                <path fill="currentColor" d="M4 17q-.425 0-.712-.288T3 16t.288-.712T4 15h12q.425 0 .713.288T17 16t-.288.713T16 17zm0-4q-.425 0-.712-.288T3 12t.288-.712T4 11h12q.425 0 .713.288T17 12t-.288.713T16 13zm0-4q-.425 0-.712-.288T3 8t.288-.712T4 7h12q.425 0 .713.288T17 8t-.288.713T16 9zm16 8q-.425 0-.712-.288T19 16t.288-.712T20 15t.713.288T21 16t-.288.713T20 17m0-4q-.425 0-.712-.288T19 12t.288-.712T20 11t.713.288T21 12t-.288.713T20 13m0-4q-.425 0-.712-.288T19 8t.288-.712T20 7t.713.288T21 8t-.288.713T20 9" />
            </svg>
        </button>
    </div>

    <div class="h-full flex justify-end gap-4 mr-4 items-center">
        <button class="{btn_shared_classes}" title="Upload" onclick={() => {}}>
            <svg class="h-8" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5">
                    <path d="M20 22H6a2 2 0 0 1-2-2m0 0a2 2 0 0 1 2-2h14V6c0-1.886 0-2.828-.586-3.414S17.886 2 16 2h-6c-2.828 0-4.243 0-5.121.879C4 3.757 4 5.172 4 8z" />
                    <path d="M19.5 18s-1 .763-1 2s1 2 1 2M9 10s2.21-3 3-3s3 3 3 3m-3-2.5V13" />
                </g>
            </svg>
        </button>
    </div>
</div>


<style>
    svg {
        margin: auto;
    }
</style>