<script lang="ts">
    import { getTextHookerOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
    import SelectOption from "$lib/components/SelectOption.svelte";
    let { onoutsideclick, presets, preset_name = $bindable() } = $props();
    let options = getTextHookerOptionsContext();
</script>

<div use:clickOutside={"button[title=Options]"} {onoutsideclick} class="w-[25rem] max-w-screen grid grid-cols-2 items-center justify-between gap-2 px-4 py-4 fixed top-13 right-3 z-9 bg-mist-800 border-mist-900 border rounded-xl">
    
    <h2 class="col-span-2 text-xl font-bold mt-4" style="margin-top:0;">Main</h2>
    
    <label for="preset">Preset</label>
    <select id="preset" bind:value={preset_name}>
        {#each presets as preset}
            <option value={preset}>{preset}</option>
        {/each}
    </select>
    
    <label for="ws_url">WebSocket URL</label>
    <input id="ws_url" type="text" bind:value={options.websocket_url}>

    <h2 class="col-span-2 text-xl font-bold mt-4">Layout</h2>

    <!-- <label for="vertical">Vertical</label>
    <input id="vertical" type="checkbox" bind:checked={options.vertical}> -->

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.vertical} options={[{name: "Vertical", value: true}, {name: "Horizontal", value: false}]} --height="2rem" />
    </div>

    <h2 class="col-span-2 text-xl font-bold mt-4">Style</h2>

    <label for="font_size">Font Size</label>
    <div class="flex items-center mx-auto border border-neutral-600 bg-neutral-600 rounded-full">
        <button onclick={() => { options.font_size-- }} class="w-7 h-7 pl-1 text-[0.7rem] rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
        <input id="font_size" type="number" bind:value={options.font_size} class="w-9 h-7 text-sm text-center hide-input-spinners z-10">
        <button onclick={() => { options.font_size++ }} class="w-7 h-7 pr-1 text-[1rem] rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
    </div>
    
</div>

<style>
    label, span {
        width: fit-content;
        margin-left:0.5rem;
    }
</style>