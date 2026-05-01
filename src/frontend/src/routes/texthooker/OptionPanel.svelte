<script lang="ts">
    import { getTextHookerOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
    let { onoutsideclick } = $props();
    let options = getTextHookerOptionsContext();
</script>

<div use:clickOutside={"button[title=Options]"} {onoutsideclick} class="w-[20rem] grid grid-cols-2 items-center justify-between gap-1 px-4 py-4 fixed top-13 right-3 z-9 bg-mist-800/90 border rounded-xl">
    <label for="preset">Preset</label>
    <select id="preset" bind:value={options.preset_name}>
        <option value="Default">Default</option>
    </select>
    
    <label for="ws_url">WebSocket URL</label>
    <input id="ws_url" type="text" bind:value={options.websocket_url}>

    <label for="vertical">Vertical</label>
    <input id="vertical" type="checkbox" bind:checked={options.vertical}>

    <label for="font_size">Font Size</label>
    <div class="flex items-center mx-auto">
        <button onclick={() => { options.font_size-- }} class="w-10 h-8 pl-1 text-[0.7rem] border rounded-l-full cursor-pointer">A</button>
        <input id="font_size" type="number" bind:value={options.font_size} class="w-10 h-8 text-center border-t border-b hide-input-spinners" >
        <button onclick={() => { options.font_size++ }} class="w-10 h-8 pr-1 text-lg border rounded-r-full cursor-pointer">A</button>
    </div>
    
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

</style>