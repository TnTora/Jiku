<script lang="ts">
    import { getTextHookerOptionsContext } from "./context";
    // let { options = $bindable() } = $props();
    let options = getTextHookerOptionsContext();
</script>

<div class="w-[20rem] grid grid-cols-2 items-center justify-between gap-1 px-4 py-4 fixed top-13 right-3 z-9 bg-mist-800/90 border rounded-xl">
    <label for="ws_url">WebSocket URL</label>
    <input id="ws_url" type="text" bind:value={options.websocket_url}>

    <label for="vertical">Vertical</label>
    <input id="vertical" type="checkbox" bind:checked={options.vertical}>

    <label for="font_size">Font Size</label>
    <input id="font_size" type="number" bind:value={options.font_size} class="mx-auto w-10" >
</div>
