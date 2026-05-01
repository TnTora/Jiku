<script lang="ts">
    import { getEbookReaderOptionsContext } from "./context";
    import Toggle from "$lib/components/Toggle.svelte";
    import { clickOutside } from "$lib/utils/clickOutside.js";


    let { onoutsideclick } = $props();
    let options = getEbookReaderOptionsContext();
    const header_style = "col-span-2 text-xl font-bold mt-4";

    function toggleOption(option: string) {
        const handle = () => { options[option] = !options[option] };
        return handle;
    }
</script>

<div use:clickOutside={"button[title=Options]"} {onoutsideclick} class="w-[30rem] grid grid-cols-[auto_auto] items-center justify-between gap-2 px-4 py-4 fixed top-13 right-3 z-20 bg-[#1B1B1B] border border-neutral-900 rounded-2xl">
    <h2 class="{header_style}" style="margin-top:0;">Layout</h2>

    <span>Vertical</span>
    <div class="toggle">
        <Toggle option={options.vertical} title={"Vertical"} height={1.25}  onclick={toggleOption("vertical")}/>
    </div>

    <!-- <label for="vertical">Vertical</label>
    <input id="vertical" type="checkbox" bind:checked={options.vertical}> -->

    <span>Paginated</span>
    <div class="toggle">
        <Toggle option={options.paginated} title={"Paginated"} height={1.25}  onclick={toggleOption("paginated")}/>
    </div>

    <!-- <label for="paginated">Paginated</label>
    <input id="paginated" type="checkbox" bind:checked={options.paginated}> -->

    <h2 class="{header_style}">Style</h2>

    <label for="font_size">Font Size</label>
    <div class="flex items-center mx-auto">
        <button onclick={() => { options.font_size-- }} class="w-7 h-7 pl-1 text-[0.7rem] border border-neutral-600 rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
        <input id="font_size" type="number" bind:value={options.font_size} class="w-9 h-7 text-sm text-center border-t border-b border-neutral-600 bg-neutral-600 hide-input-spinners" >
        <button onclick={() => { options.font_size++ }} class="w-7 h-7 pr-1 text-[1rem] border border-neutral-600 rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
    </div>

    <label for="line_height">Line Height</label>
    <div class="flex items-center mx-auto">
        <button onclick={() => { options.line_height-- }} class="w-7 h-7 pl-1 border border-neutral-600 rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600">-</button>
        <input id="line_height" type="number" bind:value={options.line_height} class="w-9 h-7 text-sm text-center border-t border-b border-neutral-600 bg-neutral-600 hide-input-spinners">
        <button onclick={() => { options.line_height++ }} class="w-7 h-7 pr-1 border border-neutral-600 rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600">+</button>
    </div>

    <h2 class="{header_style}">Extra</h2>

    <span>Show Progress</span>
    <div class="toggle">
        <Toggle option={options.show_progress} title={"Show Progress"} height={1.25}  onclick={toggleOption("show_progress")}/>
    </div>

    <!-- <label for="show_progress">Show Progress</label>
    <input id="show_progress" type="checkbox" bind:checked={options.show_progress}> -->

    <span>Show progress just for current section</span>
    <div class="toggle">
        <Toggle option={options.limit_progress_to_section} title={"Show progress just for current section"} height={1.25}  onclick={toggleOption("limit_progress_to_section")}/>
    </div>

    <!-- <label for="limit_progress_to_section">Show progress just for current section</label>
    <input id="limit_progress_to_section" type="checkbox" bind:checked={options.limit_progress_to_section}> -->
    
    
</div>

<style>
    .hide-input-spinners {
        -moz-appearance: textfield;
        appearance: textfield;
    }

    .hide-input-spinners::-webkit-outer-spin-button,
    .hide-input-spinners::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    label {
        width: fit-content;
        margin-left:0.5rem;
    }

    /* input {
        width: 2.5rem;
        margin-inline: auto;
    } */

    .toggle {
        margin-inline: auto;
    }

</style>