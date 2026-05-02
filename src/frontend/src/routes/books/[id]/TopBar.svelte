<script>
    let { title, toggleOptions, toggleSidePanel, toggleJumpBox, toggleBookmarking} = $props();
    let btn_shared_classes = "hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";
</script>

<div class="bg-neutral-800 h-11 w-full fixed top-0 grid grid-cols-[1fr_auto_1fr] items-center gap-x-1.5 z-20">
    <div class="h-full flex justify-start gap-4 ml-4 items-center">
        <button class="{btn_shared_classes}" title="TOC" onclick={toggleSidePanel}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8" viewBox="0 0 24 24">
                <path fill="currentColor" d="M4 17q-.425 0-.712-.288T3 16t.288-.712T4 15h12q.425 0 .713.288T17 16t-.288.713T16 17zm0-4q-.425 0-.712-.288T3 12t.288-.712T4 11h12q.425 0 .713.288T17 12t-.288.713T16 13zm0-4q-.425 0-.712-.288T3 8t.288-.712T4 7h12q.425 0 .713.288T17 8t-.288.713T16 9zm16 8q-.425 0-.712-.288T19 16t.288-.712T20 15t.713.288T21 16t-.288.713T20 17m0-4q-.425 0-.712-.288T19 12t.288-.712T20 11t.713.288T21 12t-.288.713T20 13m0-4q-.425 0-.712-.288T19 8t.288-.712T20 7t.713.288T21 8t-.288.713T20 9" />
            </svg>
        </button>
        <button class="{btn_shared_classes}" title="Close">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5" viewBox="0 0 15 15">
                <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
            </svg>
        </button>
    </div>

    <div class="text-xs text-neutral-500 bg-neutral-800/95 px-2 py-1 rounded-full z-10">{title}</div>

    <div class="h-full flex justify-end gap-4 mr-4 items-center">
        <button class="{btn_shared_classes}" title="Bookmark" onclick={toggleBookmarking}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M18 2H6c-1.1 0-2 .9-2 2v17c0 .36.19.69.5.87s.69.18 1 0l6.5-3.72l6.5 3.72c.15.09.33.13.5.13s.35-.04.5-.13c.31-.18.5-.51.5-.87V4c0-1.1-.9-2-2-2" />
            </svg>
        </button>
        <button class="{btn_shared_classes}" title="Jump To" onclick={toggleJumpBox}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 32 32">
                <path fill="currentColor" d="M13.414 17.586L18 22.172V8H8V6h10a2 2 0 0 1 2 2v14.172l4.586-4.586L26 19l-7 7l-7-7Z" />
            </svg>
        </button>
        <button class="{btn_shared_classes}" title="Options" onclick={toggleOptions}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5" viewBox="0 0 512 512">
                <path fill="currentColor" d="M495.9 166.6c3.2 8.7.5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6c-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2c-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8c-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4l-55.6 17.8c-8.8 2.8-18.6.3-24.5-6.8c-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3c-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4c-1.1-8.4-1.7-16.9-1.7-25.5s.6-17.1 1.7-25.4l-43.3-39.4c-6.9-6.2-9.6-15.9-6.4-24.6c4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2c5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8c8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336a80 80 0 1 0 0-160a80 80 0 1 0 0 160" />
            </svg>
        </button>
    </div>
</div>


<style>
    svg {
        margin: auto;
    }
</style>